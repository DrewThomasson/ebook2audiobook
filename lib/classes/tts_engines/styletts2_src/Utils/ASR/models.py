import math
import torch
from torch import nn
from torch.nn import TransformerEncoder
import torch.nn.functional as F
from .layers import MFCC, Attention, LinearNorm, ConvNorm, ConvBlock

class ASRCNN(nn.Module):
    def __init__(self,
                 input_dim=80,
                 hidden_dim=256,
                 n_token=35,
                 n_layers=6,
                 token_embedding_dim=256,

    ):
        super().__init__()
        self.n_token = n_token
        self.n_down = 1
        self.to_mfcc = MFCC()
        self.init_cnn = ConvNorm(input_dim//2, hidden_dim, kernel_size=7, padding=3, stride=2)
        self.cnns = nn.Sequential(
            *[nn.Sequential(
                ConvBlock(hidden_dim),
                nn.GroupNorm(num_groups=1, num_channels=hidden_dim)
            ) for n in range(n_layers)])
        self.projection = ConvNorm(hidden_dim, hidden_dim // 2)
        self.ctc_linear = nn.Sequential(
            LinearNorm(hidden_dim//2, hidden_dim),
            nn.ReLU(),
            LinearNorm(hidden_dim, n_token))
        self.asr_s2s = ASRS2S(
            embedding_dim=token_embedding_dim,
            hidden_dim=hidden_dim//2,
            n_token=n_token)

    def forward(self, x, src_key_padding_mask=None, text_input=None):
        x = self.to_mfcc(x)
        x = self.init_cnn(x)
        x = self.cnns(x)
        x = self.projection(x)
        x = x.transpose(1, 2)
        ctc_logit = self.ctc_linear(x)
        if text_input is not None:
            _, s2s_logit, s2s_attn = self.asr_s2s(x, src_key_padding_mask, text_input)
            return ctc_logit, s2s_logit, s2s_attn
        else:
            return ctc_logit

    def get_feature(self, x):
        x = self.to_mfcc(x.squeeze(1))
        x = self.init_cnn(x)
        x = self.cnns(x)
        x = self.projection(x)
        return x

    def length_to_mask(self, lengths):
        mask = torch.arange(lengths.max()).unsqueeze(0).expand(lengths.shape[0], -1).type_as(lengths)
        mask = torch.gt(mask+1, lengths.unsqueeze(1)).to(lengths.device)
        return mask

    def get_future_mask(self, out_length, unmask_future_steps=0):
        """
        Args:
            out_length (int): returned mask shape is (out_length, out_length).
            unmask_futre_steps (int): unmasking future step size.
        Return:
            mask (torch.BoolTensor): mask future timesteps mask[i, j] = True if i > j + unmask_future_steps else False
        """
        index_tensor = torch.arange(out_length).unsqueeze(0).expand(out_length, -1)
        mask = torch.gt(index_tensor, index_tensor.T + unmask_future_steps)
        return mask

class ASRS2S(nn.Module):
    def __init__(self,
                 embedding_dim=256,
                 hidden_dim=512,
                 n_location_filters=32,
                 location_kernel_size=63,
                 n_token=40):
        super(ASRS2S, self).__init__()
        self.embedding = nn.Embedding(n_token, embedding_dim)
        val_range = math.sqrt(6 / hidden_dim)
        self.embedding.weight.data.uniform_(-val_range, val_range)

        self.decoder_rnn_dim = hidden_dim
        self.project_to_n_symbols = nn.Linear(self.decoder_rnn_dim, n_token)
        self.attention_layer = Attention(
            self.decoder_rnn_dim,
            hidden_dim,
            hidden_dim,
            n_location_filters,
            location_kernel_size
        )
        self.decoder_rnn = nn.LSTMCell(self.decoder_rnn_dim + embedding_dim, self.decoder_rnn_dim)
        self.project_to_hidden = nn.Sequential(
            LinearNorm(self.decoder_rnn_dim * 2, hidden_dim),
            nn.Tanh())
        self.sos = 1
        self.eos = 2

    def initialize_decoder_states(self, memory, mask):
        """
        moemory.shape = (B, L, H) = (Batchsize, Maxtimestep, Hiddendim)
        """
        B, L, H = memory.shape
        self.decoder_hidden = torch.zeros((B, self.decoder_rnn_dim)).type_as(memory)
        self.decoder_cell = torch.zeros((B, self.decoder_rnn_dim)).type_as(memory)
        self.attention_weights = torch.zeros((B, L)).type_as(memory)
        self.attention_weights_cum = torch.zeros((B, L)).type_as(memory)
        self.attention_context = torch.zeros((B, H)).type_as(memory)
        self.memory = memory
        self.processed_memory = self.attention_layer.memory_layer(memory)
        self.mask = mask
        self.unk_index = 3
        self.random_mask = 0.1

    def forward(self, memory, memory_mask, text_input):
        """
        moemory.shape = (B, L, H) = (Batchsize, Maxtimestep, Hiddendim)
        moemory_mask.shape = (B, L, )
        texts_input.shape = (B, T)
        """
        self.initialize_decoder_states(memory, memory_mask)
        # text random mask
        random_mask = (torch.rand(text_input.shape) < self.random_mask).to(text_input.device)
        _text_input = text_input.clone()
        _text_input.masked_fill_(random_mask, self.unk_index)
        decoder_inputs = self.embedding(_text_input).transpose(0, 1) # -> [T, B, channel]
        start_embedding = self.embedding(
            torch.LongTensor([self.sos]*decoder_inputs.size(1)).to(decoder_inputs.device))
        decoder_inputs = torch.cat((start_embedding.unsqueeze(0), decoder_inputs), dim=0)

        hidden_outputs, logit_outputs, alignments = [], [], []
        while len(hidden_outputs) < decoder_inputs.size(0):

            decoder_input = decoder_inputs[len(hidden_outputs)]
            hidden, logit, attention_weights = self.decode(decoder_input)
            hidden_outputs += [hidden]
            logit_outputs += [logit]
            alignments += [attention_weights]

        hidden_outputs, logit_outputs, alignments = \
            self.parse_decoder_outputs(
                hidden_outputs, logit_outputs, alignments)

        return hidden_outputs, logit_outputs, alignments


    def decode(self, decoder_input):

        cell_input = torch.cat((decoder_input, self.attention_context), -1)
        self.decoder_hidden, self.decoder_cell = self.decoder_rnn(
            cell_input,
            (self.decoder_hidden, self.decoder_cell))

        attention_weights_cat = torch.cat(
            (self.attention_weights.unsqueeze(1),
            self.attention_weights_cum.unsqueeze(1)),dim=1)

        self.attention_context, self.attention_weights = self.attention_layer(
            self.decoder_hidden,
            self.memory,
            self.processed_memory,
            attention_weights_cat,
            self.mask)

        self.attention_weights_cum += self.attention_weights

        hidden_and_context = torch.cat((self.decoder_hidden, self.attention_context), -1)
        hidden = self.project_to_hidden(hidden_and_context)

        # dropout to increasing g
        logit = self.project_to_n_symbols(F.dropout(hidden, 0.5, self.training))

        return hidden, logit, self.attention_weights

    def parse_decoder_outputs(self, hidden, logit, alignments):

        # -> [B, T_out + 1, max_time]
        alignments = torch.stack(alignments).transpose(0,1)
        # [T_out + 1, B, n_symbols] -> [B, T_out + 1,  n_symbols]
        logit = torch.stack(logit).transpose(0, 1).contiguous()
        hidden = torch.stack(hidden).transpose(0, 1).contiguous()

        return hidden, logit, alignments
