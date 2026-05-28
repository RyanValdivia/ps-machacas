from django.db import models

class OpticalCenter(models.Model):
    optNom = models.CharField(max_length=255)
    optLema = models.CharField(max_length=255, blank=True, null=True)
    optDir = models.TextField(blank=True, null=True)
    optProv = models.TextField(blank=True, null=True)
    optTel = models.CharField(max_length=15, blank=True, null=True)
    optLogo = models.ImageField(upload_to="company/", blank=True, null=True) #Funciona con Pillow

    def save(self, *args, **kwargs):
        self.pk = 1  
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # evita borrado accidental

    def __str__(self):
        return "Configuración General de la Empresa"