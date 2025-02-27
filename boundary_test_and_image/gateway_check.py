from param_constraints import ParamConstraints
from image_video_detect import Detection
import base64
import binascii
import cv2
import numpy as np
import io
import sys

cp = ParamConstraints()
det = Detection()

class GatewayCheck:
    #check a name is legal or illegal
    def check_a_param_name(self,name):
        return cp.check_name(name)

    #Check the parameters name is legal or illegal
    def check_all_param_name(self,request):
        for key in request.keys():
            if cp.check_name(key) == False:
                return False
        return True

    #check a string whether in base64 or not
    def is_base64(self,param):
        try:
            base64.b64decode(param)
            return True
        except:
            return False
    
    #detect the type of param
    def detect_type(self,param):
        if(type(param).__name__ == 'str'):
            return 'str'
        if type(param).__name__ == 'int':
            return 'int'
        if type(param).__name__ == 'float':
            return 'float'
        else:
            if det.detect(param) == 'img':
                return 'img'
            elif det.detect(param) == 'video':
                return 'video'
            else:
                return False
        return False

    #Check a param inbound or outbound of constraints
    def check_inbound(self,constraints, param):
        const = constraints
        if(const['param_limit_type']=='size'):
            if const['param_name'] in ['image','video']:
                if self.get_size(param) > int(const['param_limit_min']) and self.get_size(param) < int(const['param_limit_max'])*1024*1024:
                    return True
                else:
                    return False
            else:
                if int(param) > int(const['param_limit_min']) and int(param) < int(const['param_limit_max']):
                    return True
                else:
                    return False
        else:
            if const['param_name'] == 'image':
                if self.is_base64(param) == False:
                    print("Param not a base64")
                    return False
            if len(param) >= int(const['param_limit_min']) and len(param) <= int(const['param_limit_max']):
                return True

    #check a constraints of a param name and it's type is legal or illegal
    def check_paramname_param(self,param_name,param):
        if self.check_a_param_name(param_name) == False:
            return False
        constraints = cp.get_constraints_by_name_type(param_name,self.detect_type(param))
        if(constraints['param_type'] == self.detect_type(param)):
            if self.check_inbound(constraints,param):
                print("The param {} is inbound".format(param_name))
                return True
            else:
                print("The param '{}' is outbound".format(param_name))
                return False
        else:
            print("The param's name '{}' not accept this file type".format(param_name))
            False

    #check the size of file from buffer
    def get_size(self,param):
        byteslist = []
        while(param.read(1)):
            byteslist.append(param.read(1))
        param.seek(0, 0)
        return len(byteslist)*2