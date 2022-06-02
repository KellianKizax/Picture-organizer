cat_folder = "Boucle Oreilles"

words = cat_folder.split(' ')
ref = ""
for w in words:
    ref += w[0].lower()

print(ref)