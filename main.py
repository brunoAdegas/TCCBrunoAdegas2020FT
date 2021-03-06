
from tkinter import *
from tkinter import filedialog
import nltk as nltk
import csv
import unicodedata
import re
from nltk.corpus import stopwords
from tkinter import messagebox as mb
from operator import itemgetter, attrgetter
#nltk.download('rslp')
#nltk.download('stopwords')


if __name__ == '__main__':

    class Application:
        def __init__(self, master=None):

            def inserirPalavraChave():
                palavraChaveInput = palavraChaveEntry.get()
                setPCBrutas = set(palavraChaveInput.split())
                setPCLimpas = stemmingPC(setPCBrutas)
                listaPC["text"] = setPCLimpas
                return setPCLimpas

            #Pré-processamento das palavras chaves inseridas pelo professor
            def stemmingPC(setPCBrutas):
                stemPC = nltk.stem.RSLPStemmer()
                listaPCLimpas = []
                for w in setPCBrutas:
                    stemmingPC = stemPC.stem(w)
                    listaPCLimpas.append(stemmingPC)
                return listaPCLimpas

            def removerAcentosECaracteres(resposta):
                nfkd = unicodedata.normalize('NFKD', resposta)
                respostaNormalizada = u"".join([c for c in nfkd if not unicodedata.combining(c)])
                return re.sub('[^a-zA-Z0-9 \\\]', '', respostaNormalizada)

            #Pré-processamento das palavras inclusas nas respostas dos alunos
            def stemmingResposta(listaRespostas):
                stemResposta = nltk.stem.RSLPStemmer()
                stopwords = nltk.corpus.stopwords.words('portuguese')
                for w in listaRespostas:
                        respostaProcessadaAluno = []
                        respostaAluno = w.getRespostaAluno()
                        respostaAlunoNormalizada = removerAcentosECaracteres(respostaAluno)
                        listaPalavrasRespostaAluno = set(respostaAlunoNormalizada.split())
                        listaPalavrasRespostaAlunoSemStopWord = [palavra for palavra in listaPalavrasRespostaAluno if palavra not in stopwords]
                        for j in listaPalavrasRespostaAlunoSemStopWord:
                            stemminResposta = stemResposta.stem(j)
                            respostaProcessadaAluno.append(stemminResposta)
                        w.setRespostaAlunoProcessada(respostaProcessadaAluno)
                        print("Resposta Processada:", w.getRespostaAlunoProcessada())
                return listaRespostas

            #calculo da distancia de Jaccard
            def calcularDistanciaJaccard(listaRespostasLimpas):
                listaPCLimpas = inserirPalavraChave()
                for w in listaRespostasLimpas:
                    numPalavrasResposta = 0
                    resposta = w.getRespostaAlunoProcessada()
                    for n in listaPCLimpas:
                        print("resp", resposta)
                        contadorPC = resposta.count(n)
                        print(n , "qtd ", contadorPC)
                        numPalavrasResposta = contadorPC + numPalavrasResposta
                    w.setNumPalavrasUsadas(numPalavrasResposta)
                    print(w.getRespostaAluno())
                    setResposta = set(w.getRespostaAlunoProcessada())
                    setConceito = set(listaPCLimpas)
                    print("lista palavras-chave:", setConceito)
                    distJaccard = float(len(setConceito & setResposta)) / len(setConceito | setResposta)
                    w.setCoeficiente(distJaccard)
                    print("Valor coeficiente Jaccard:", distJaccard)
                    mensagem = ("RA: {idAluno}\nResposta Completa: {respCompleta}\nResposta Processada: {resp}\nCoeficiente: {sim:.2f}\nNúmero de Palavras-Chave na resposta: {num}")\
                                                                                                                                               .format(idAluno=w.getId(),
                                                                                                                                               respCompleta=w.getRespostaAluno(),
                                                                                                                                               resp=w.getRespostaAlunoProcessada(),
                                                                                                                                               sim=w.getCoefieciente(),
                                                                                                                                               num=numPalavrasResposta)
                    mb.showinfo("Similaridade das Respostas", mensagem)
                stringPrint = " "
                #ordenar as respostas de maior similaridade para menor
                listaSorted = sorted(listaRespostasLimpas, key=attrgetter('coeficiente'), reverse=True)
                for x in listaSorted:
                    ra = x.id
                    resp = x.respostaAluno
                    coe = x.coeficiente
                    numP = x.numPalavrasUsadas
                    stringRA = ("RA: {idAluno}").format(idAluno=ra)
                    stringResp = ("Resposta: {respComp}").format(respComp=resp)
                    stringCoef = ("Coeficiente: {coeF:.2f}").format(coeF=coe)
                    stringNumP = ("Número Palavras-Chave: {num}").format(num=numP)
                    listaRespostasPrint.insert(END, stringRA)
                    listaRespostasPrint.insert(END, stringResp)
                    listaRespostasPrint.insert(END, stringCoef)
                    listaRespostasPrint.insert(END, stringNumP)
                    listaRespostasPrint.insert(END, "<-------------------------------------------------------->")
                listaRespostasPrint.configure(justify="left")
                #colocar scroll na lista de respostas


            #abre o explorador de arquivos para escolher o arquivo de respostas e já manda calcular a similaridade a partir dos dados contidos no arquivo
            def browseFiles():
                filename = filedialog.askopenfilename(initialdir="/",
                                                      title="Selecione o arquivo de respostas",
                                                      filetypes=(("Arquivo CSV",
                                                                  "*.csv*"),
                                                                 ("Arquivo de Texto",
                                                                  "*.txt*")
                                                                 ))
                labelArquivoSelecionado["text"] = ("Arquivo selecionado: " + filename)
                arquivo = open(filename, 'r', encoding="utf8")
                reader = csv.DictReader(arquivo)
                listaRespostas = []
                for linha in reader:
                    print("RA:", linha['id'], "Resposta:", linha['resposta'])
                    idAluno = linha['id']
                    respostaAluno = linha['resposta']
                    newResposta = Resposta(idAluno, respostaAluno, 0, " ", 0)
                    listaRespostas.append(newResposta)
                listaRespostasLimpas = stemmingResposta(listaRespostas)
                calcularDistanciaJaccard(listaRespostasLimpas)
                return listaRespostas

            #definição da classe Resposta
            class Resposta:
                def __init__(self, id, respostaAluno, respostaAlunoProcessada, coeficiente, numPalavrasUsadas):
                    self.id = id
                    self.respostaAluno = respostaAluno
                    self.respostaAlunoProcessada = respostaAlunoProcessada
                    self.coeficiente = coeficiente
                    self.numPalavrasUsadas =numPalavrasUsadas

                def setId(self, id):
                    self.id = id

                def setRespostaAluno(self, respostaAluno):
                    self.respostaAluno = respostaAluno

                def setRespostaAlunoProcessada(self, respostaAlunoProcessada):
                    self.respostaAlunoProcessada = respostaAlunoProcessada

                def setCoeficiente(self, coeficiente):
                    self.coeficiente = coeficiente

                def setNumPalavrasUsadas(self, numPalavrasUsadas):
                    self.numPalavrasUsadas = numPalavrasUsadas

                def getId(self):
                    return self.id

                def getRespostaAluno(self):
                    return self.respostaAluno

                def getRespostaAlunoProcessada(self):
                    return self.respostaAlunoProcessada

                def getCoefieciente(self):
                    return self.coeficiente

                def getNumPalavrasUsadas(self):
                    return self.numPalavrasUsadas


             #definição dos elementos gráficos
            labelEntryPalavraChave = Label(root,
                                           text="Digite as Palavras-Chave esperadas nas respostas",
                                           width=50, height=4,
                                           fg="blue")

            palavraChaveEntry = Entry(root,
                                      width=50,
                                      fg="red",
                                      relief=RIDGE)

            buttonInserePalavraChave = Button(root,
                                       text="Inserir Palavras-Chave",
                                       command= inserirPalavraChave,
                                       justify="center"
                                       )

            listaPC = Label(root,
                            text="",
                            height=4)

            labelListaPC = Label(root,
                                 text="Lista de Palavras-Chave:",
                                 width=20, height=4)

            buttonInsereArquivoResposta= Button(root,
                                                text="Selecionar Arquivo de Respostas",
                                                command=browseFiles)

            labelArquivoSelecionado = Label(root,
                                            text="",
                                            width=100, height=4)

            labelRespostas = Label(root,
                                   text="Lista Respostas",
                                   width=20, height=4)

            listaRespostasPrint = Listbox(root,
                                          yscrollcommand=scrollbar.set,
                                          xscrollcommand=scrollbar.set,
                                          width=100,
                                          relief=RIDGE
                                          )

            #grid dos elementos gráficos
            labelEntryPalavraChave.grid(column=0, row=0)
            palavraChaveEntry.grid(column=0, row=1)
            buttonInserePalavraChave.grid(column=0, row=2)
            labelListaPC.grid(column=0, row=3)
            listaPC.grid(column=0, row=4)
            buttonInsereArquivoResposta.grid(column=0, row=5)
            labelArquivoSelecionado.grid(column=0, row=6)
            labelRespostas.grid(column=0, row=7)
            listaRespostasPrint.grid(column=0, row=8)

    root = Tk()
    scrollbar = Scrollbar(root)
    Application(root)
    root.title("Prototipo De Assistência Ao Docente")
    root.geometry("700x700")
    root.mainloop()


