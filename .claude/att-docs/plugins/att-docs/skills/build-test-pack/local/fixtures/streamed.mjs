// A streamed chat reply as Lemonade sends one: a role chunk, the thinking and the
// content in deltas, a chunk with the finish reason, a usage chunk with no
// choices (and the `timings` block, when a test gives one), then [DONE]. `sse` gives the
// text, `streamed` a fetch-shaped reply, and `firstEvent` the role chunk a server sends as
// soon as it starts the reply.

const event = (chunk) => `data: ${JSON.stringify(chunk)}\n\n`;
const delta = (fields, finish = null) => ({ object: 'chat.completion.chunk',
  choices: [{ index: 0, delta: fields, finish_reason: finish }] });

export const firstEvent = () => event(delta({ role: 'assistant', content: null }));

export function sse({ content = '{}', finish = 'stop', usage = {}, reasoning = '', timings = null } = {}) {
  const half = Math.ceil(content.length / 2);
  return [
    firstEvent(),
    ...(reasoning ? [event(delta({ reasoning_content: reasoning }))] : []),
    event(delta({ content: content.slice(0, half) })),
    event(delta({ content: content.slice(half) })),
    event(delta({}, finish)),
    event({ object: 'chat.completion.chunk', choices: [], usage, ...(timings ? { timings } : {}) }),
    'data: [DONE]\n\n',
  ].join('');
}

export function streamed(reply) {
  const text = sse(reply);
  return { ok: true, status: 200, text: async () => text };
}
