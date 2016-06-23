class Twitt:
	def __init__(self, classe, data, texto):
		self.classe = classe
		self.data = data
		self.texto = texto

	def addTexto(self, texto):
		self.texto = self.texto+' '+texto