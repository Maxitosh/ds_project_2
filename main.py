import pickle

msg = {"command":'send'}

print(pickle.dumps(msg))

str = b'\x80\x04\x95\x15\x00\x00\x00\x00\x00\x00\x00}\x94\x8c\x07command\x94\x8c\x04send\x94s.'

print(pickle.load(str))