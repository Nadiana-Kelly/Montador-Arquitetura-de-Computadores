import struct
#Anotações
#O bytearray(b'\x01\x02\x03\x04\x05') coloca os valores em hex
#O '<I'serve pra usar estilo Little endian

comandosI = {'nop': 0x01, 'iadd': 0x02,'isub': 0x05,'iand': 0x08,'ior': 0x0B,'dup': 0x0E,'pop': 0x10,'swap': 0x13,'bipush': 0x19,'iload': 0x1C, 'istore': 0x22, 'wide': 0x28, 'ldc_w': 0x32, 'iinc': 0x36,'goto': 0x3C,'iflt': 0x43,'ifeq': 0x47, 'if_icmpeq': 0x4B,'invokevirtual': 0x55,'ireturn': 0x6B }

def checSintaxe(programa):
  labels = []
  checkFinal = True
  #Labels
  for line in programa:
    if len(line) > 1 and line[0] not in comandosI:
      labels.append(line[0])

  for line in programa:

    if len(line) == 2:
      if line[0] == "bipush":
        if line[1].isnumeric() == True:
          checkFinal= True
        else: return False
      elif line[0] == "iadd" or line[0] == "iand" or line[0] == "ior" or line[0] == "isub" or line[0] == "nop":
        return False
      elif line[0] == "if_icmpeq" or line[0] == "goto":
        if line[1] in labels:
          checkFinal = True
        else: 
          return False
      elif line[0] == "iload" or line[0] == "istore":
        
        if line[1].isnumeric() == False:
          checkFinal = True
        else: 
          return False
    if len(line) > 2:
      
      if line[1] == "bipush":
        if line[2].isnumeric() == True:
          checkFinal = True
        else: 
          return False
      else: 
        checkFinal = True
  return checkFinal

#Essa função escreve o programa no .exe;
def escreProgram(prog):
  #Essa função faz a conversão do array de bytes em bytes;
  byFinal = bytes(prog)

  #Isso serve parar escrever o arquivo final;
  with open("NadianaK.exe", 'wb') as biOutput:
    #Isso serve para escrever o texto ou bytes no arquivo;
    byEscritos = biOutput.write(byFinal)
    print("\n")
    print(f'Escritos {byEscritos} bytes')
  
def codAssembler(programa):
  #Comandos com valor de 3 bytes;
  bytesTres = ['goto', 'if_icmpeq']

  labEsq = {} #labels na esquerda - [Main: posição, rep: posição]
  labDir = {} #labels na direita - (Main: [valor], rep: [valor])
  contByte = 0 #tamanho do programa

  lista_byte = []

  variaveis = [] 

  #Enconstra  todas as labels do lado esquerdo e do lado direito
  for line in programa:
    if len(line) > 1 and line[0] not in comandosI:
      labEsq[line[0]] = 0
    if len(line)> 1 and line[0] in bytesTres:
      labDir[line[1]] = []
  print("\n")
  print("Labels na esquerda: ", labEsq)
  print("Labels na direita: ", labDir, "\n")
      
  #Calcula o tamanho do programa,labels e variáveis.
  for line in programa: 

    #Se a linha não tem label, só operador e operando.
    if len(line) == 2 and line[0] not in labEsq and line[1] not in labDir:
      if not line[1].isnumeric() and line[1] not in variaveis: 

        #Procura todas as variáveis.
        variaveis.append(line[1])
      contByte += len(line)

    #Se tem operador e label.
    elif len(line) == 2 and line[1] in labDir:
      labDir[line[1]].append(contByte + 1)

       #Mostra o valor da label em questão.
      contByte += len(line) + 1
    elif len(line) == 2 and line[0] in labEsq:
      labEsq[line[0]] = contByte + 1 
      contByte += len(line) - 1

    #Tem label, operador e operando
    elif len(line) == 3 and line[0] in labEsq:
      labEsq[line[0]] = contByte + 1 
      contByte += len(line) - 1 

    elif line[-1] not in labEsq and line[-1] not in variaveis and line[-1] not in comandosI:
      variaveis.append(line[-1])
    else: 
      contByte += len(line) 

  #Variáveis que não são numéros.
  varNoNumb = []
  for var in variaveis:
     if var.isnumeric() == False:
      varNoNumb.append(var)

  
  print("Variáveis: ", variaveis,"\n")
  print("Labels direita com  - valor  ", labDir)
  print("Labels esquerda com  - valor ", labEsq)
 
  QBytes = []
  print("\nTamanho do programa sem os 20 bytes da inicialização: " , contByte)

  prog = bytearray() 
  QBytes = struct.pack('<I', 20 + contByte)
  print("\nQ : ", QBytes[0], "\n")

  for b in QBytes:
    prog.append(b)

  
  regis = [
    0x7300, # INIT
    0x0006, # CPP
    0x1001, # LV 
    0x0400, # PC
    0x1001 + len(varNoNumb) # SP
  ]
 
  for reg in regis:
    reg = struct.pack('<I', reg)
    for regByte in reg:
      prog.append(regByte)

  #Calcula a distância entre as labels.
  calculador = 1
  checkList = []
  for line in programa:
    if len(line) > 1 and line[0] not in comandosI:
      calculador -= 1
    if line[0] in bytesTres:
      if line[1] not in checkList:
        checkList.append(line[1])
        label = line[1]
        for i in range(0, len(labDir[line[1]])):
          labDir[label][i] = labEsq[label] - labDir[label][i]
      calculador += 1
    for i in line:
      calculador += 1

  print("\nLabels com suas distâncias: ", labDir)
  print("\n")
  #Traduzindo o programa...
  for line in programa:  
    for i in line:
      if i in comandosI:
        prog.append(int(comandosI[i]))
      elif i.isnumeric() == True:
        prog.append(int(i))
      elif i in varNoNumb:
        prog.append(int(varNoNumb.index(i)))
    if len(line) > 1:
      if line[1] in labDir:
        label = line[1]
        #Altera o número negativo em um hexa equivalente.
        valorIni = hex(labDir[label][0] & (2**16-1)) 
        
        #de hex para int
        valorFim = int(valorIni, 16) 
        valorConvert = struct.pack('>I', valorFim) 
        #O '>I' vai para Big endian
        for b in range(2, len(valorConvert)):
          prog.append(int(valorConvert[b]))
        del labDir[label][0]
        print("Lista - label direita: ", valorConvert)
      
  print("\nPrograma final: ", prog)
  escreProgram(prog)
      

def Main():

  programa = []
  with open("assembly.txt", 'r') as programa:
    programa = [line.split() for line in programa]
    
  print("Resultado da checação: ", checSintaxe(programa))
  if checSintaxe(programa) == True:
    print("Tudo ok!")
    codAssembler(programa)
  else:
    print("Error: Seu programa está com algum erro por favor refaça- o tente novamente mais tarde! ")

Main()



