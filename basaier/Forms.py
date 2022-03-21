from django import forms
from .models import Project



# from .models import  signup


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['location']
        widgets = {
            'location': forms.TextInput(attrs={'class':'form-control','style':'width:80%; border-radius:20px'})
        }
		    
		        
		        
			        
		    
        
        
		
		
		
		