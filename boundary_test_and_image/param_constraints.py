# pip install ConfigParser (auto get verison 5.0.0)
import configparser


class ParamConstraints:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('param_boundaries.cfg')

    def get_constraints_by_name(self,name):
        result_dict = {}
        if name == 'image':
            result_dict={
            'image_type': {
                'param_name':self.config['image_image']['param_name'],
                'param_type':self.config['image_image']['param_type'],
                'param_limit_type':self.config['image_image']['param_limit_type'],
                'param_limit_min':self.config['image_image']['param_limit_min'],
                'param_limit_max':self.config['image_image']['param_limit_max'],
            },
            'string_type': {
                'param_name':self.config['image_string']['param_name'],
                'param_type':self.config['image_string']['param_type'],
                'param_limit_type':self.config['image_string']['param_limit_type'],
                'param_limit_min':self.config['image_string']['param_limit_min'],
                'param_limit_max':self.config['image_string']['param_limit_max'],
            }
            }
        else:
            result_dict['param_name']=self.config[name]['param_name']
            result_dict['param_type']=self.config[name]['param_type']
            result_dict['param_limit_type']=self.config[name]['param_limit_type']
            result_dict['param_limit_min']=self.config[name]['param_limit_min']
            result_dict['param_limit_max']=self.config[name]['param_limit_max']
        return result_dict
    
    def get_constraints_by_name_type(self,param_name,param_type):
        if(param_name=='image'):
            if(param_type=='str'):
                return self.get_constraints_by_name('image_string')
            else:
                return self.get_constraints_by_name('image_image')
        return self.get_constraints_by_name(param_name)

    def check_name(self,name):
        try:
            if name == 'image':
                return True
            else:
                self.get_constraints_by_name(name)
                return True
        except KeyError:
            return False