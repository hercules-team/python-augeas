import augeas

a = augeas.augeas()

for i in a.match("/files/etc/hosts/*"):
	for attr in a.match(i+"/*"):
                print attr, a.get(attr)
