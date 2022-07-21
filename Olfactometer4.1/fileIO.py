# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 09:29:58 2015

@author: njhall
"""
import csv 

#Simple module to open files, return a requested value, change a value, 
#create a data sheet or save a data sheet
class fileIO ():
    
    def __init__(self, path):
        
        self.path=path
    
    
    def create(self, header):
        with self. __waitforOpen(self.path, 'w') as csvfile:
            writer= csv.writer(csvfile)
            writer.writerow(header)
         

  
    def save_all(self,  data):
        with self. __waitforOpen(self.path, 'w') as csvfile:
            writer= csv.writer(csvfile)
            for row in data:
                writer.writerow(row)
            

    def get_text(self):
        with self. __waitforOpen(self.path, 'r') as f:
            return f.readline().rstrip()
            
            
    def write_path(self, val):
        with self. __waitforOpen(self.path, 'w') as f:
            f.write(val)
      
      
      
    def lookup(self, returnval, key1, key2=0) :    
        with self. __waitforOpen(self.path, 'r') as csvfile:
            info='no match'
            reader=csv.reader(csvfile)           
            for row in reader:
                if str(key1) in row:
                    if key2==0:
                        info=row[returnval]
                        break
                    else: 
                        if row[1]==str(key2):
                            info=row[returnval]
                            break
                        else:
                            info="I don't know what's going on"    
            
        return info


            
    def appendrow(self, data):
        with self. __waitforOpen(self.path, 'a') as csvfile:
            writer=csv.writer(csvfile)
            writer.writerow(data)
        
        
        
    def updatevalue (self, key1, key2, newval):
        tempdata=[]
        with self. __waitforOpen(self.path, 'r') as csvfile:
            reader=csv.reader(csvfile)           
            for row in reader:
                tempdata.append(row)
                if key1 in row:
                    row[key2]=newval
         
        self.save_all(tempdata)
                       
        
            
    def printdata(self, returnval, key1, key2=None) :    
        with self. __waitforOpen(self.path, 'r') as csvfile:
            data=[]
            reader=csv.reader(csvfile)           
            for row in reader:
                data.append(row)
        return data
        
    
    def __waitforOpen(self, path, method):
        exitflag=0
        
        while exitflag<1:
            try: 
                f= open(path, method, newline='')
                exitflag=1   
                
            except IOError:
                print ('cannot open')
                exitflag=1
                f=0
            except:
                print("open error")
                exitflag=1
                

        return f
        
       
def test():
    dog_info=fileIO('dog_info.csv')
    print(dog_info.lookup(3, "Test"))
    dog_info.appendrow([['one', 'two', 'three', 'four'], ['row2', 'row2', 'row2']])
    dog_info.appendrow([['one', 'two', 'three', 'four'], ['row2', 'row2', 'row2']])



if __name__ == "__main__": test()