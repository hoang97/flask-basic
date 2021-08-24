a = {
    'a':'1',
    'b':'2'
}
# a.values() = [3,4]
print(a)

class test:
    name = ''

    def init(self):
        pass
    
    @classmethod
    def all_attrs(cls):
        attrs = [{name: attr} for name, attr in cls.__dict__.items() if (not name.startswith('_')) and (not callable(attr)) and (not type(attr) is classmethod)]
        return attrs
        
print(test.all_attrs())