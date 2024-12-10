from broai.greeting import yo_bro


def test_yo_bro():
    assert yo_bro() == {"response": "Yo Bro!"}