

#__name__ = "__main__"
from anesplot import record_main

#print(dir())

print('-'*10)
print('this is {} file and __name__ is {}'.format('__main__', __name__))
print('this is {} file and __package__ is {}'.format('__main__', __package__))
print('-'*10)


if __name__ == '__main__':
     record_main.main()
 # ie import the module from the top level package   