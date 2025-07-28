from unittest.mock import patch
import io

from scigetup.__main__ import main

def test_main_prints_hello():
    with patch('sys.stdout', new=io.StringIO()) as fake_out:
        main()
        assert fake_out.getvalue() == "Hello from scigetup!\n"
