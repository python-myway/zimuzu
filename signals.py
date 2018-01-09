from blinker import Namespace


_signals = Namespace()


send_update_email = _signals.signal('send_update_email')