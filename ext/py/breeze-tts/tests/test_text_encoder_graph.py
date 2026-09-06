from models.text_encoder_graph import TextEncoderGraphCache


def test_smallest_fitting_key_reuses_larger_token_bucket() -> None:
    keys = ((4, 32), (4, 64), (4, 96), (4, 128), (4, 160), (4, 256))

    assert TextEncoderGraphCache._smallest_fitting_key(
        keys, batch_size=4, token_length=192
    ) == (4, 256)


def test_smallest_fitting_key_does_not_cross_batch_sizes() -> None:
    keys = ((1, 256), (2, 256), (4, 160))

    assert (
        TextEncoderGraphCache._smallest_fitting_key(
            keys, batch_size=4, token_length=192
        )
        is None
    )
