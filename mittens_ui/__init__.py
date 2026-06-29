from .mittens_ui import MittensUI
app = Krita.instance()
ext = MittensUI(parent=app)
app.addExtension(ext)
