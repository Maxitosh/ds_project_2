import pickle
import base64


str = []
with open("ClientConsoleDir/meme.jpg", 'rb') as file:
    str.append(base64.b64encode(file.read()))

print(str)

fh = open("imageToSave.jpg", "wb")
for s in str:
    print(base64.b64decode(s))
    fh.write(base64.b64decode(s))
fh.close()

msg = {"command":'send'}

# print(pickle.dumps(msg))
