#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

# unos podataka iz OpenStack konfiguracije
image = raw_input('Enter image name (default. ubuntuCloud14): ') or 'ubuntuCloud14'
flavor = raw_input('Enter flavor (default. m1.small): ') or 'm1.small'
key = raw_input('Enter key pair name (default. my_key1): ') or 'my_key1'
private_network = raw_input('Enter private network name (default. my_net1): ') or 'my_net1'
public_network = raw_input('Enter public network name (default. admin_floating_net): ') or 'admin_floating_net'

# unos broja instanci
while(1):
	try:
		count = int(input('Unesite broj instanci: '))
		print('Broj instanci je ' + str(count))
		break
	except NameError:
		print('Pogresan unos!\n')
	except SyntaxError:
		print('Pogresan unos!\n')

# kreiranje veza medu instancama
connections = []

# kreiranje prazne liste od #count podliste
for i in range(count):
	connections.append([])

# upisivanje veza medu instancama u listu
i = 0
while(i < count):
	line = raw_input('Instanca ' + str(i + 1) + ' komunicira sa (format. "1 2 3 ..."): ')
	lines = line.split()
	for j in lines:
		try:
			connections[i].append(int(j) - 1)
		except ValueError:
			print("Pogresan unos!\n")
			i = i - 1
			break
	i = i + 1

# stvaranje prazne liste za mysql
mysql = []
for i in range(count):
	mysql.append(None)

# dodavanje vrijednosti true/false za mysql
flag = 0
while(flag == 0):
	flag = 1
	databases = raw_input('Instance koje zahtijevaju bazu podataka (format. "1 2 3 ..."): ').split()
	for i in databases:
		try:
			mysql[int(i) - 1] = True
		except ValueError:
			print("Pogresan unos!\n")
			flag = 0
			break
		except IndexError:
			print("Pogresan unos!\n")
			flag = 0
			break

# direktorij sa template-ima
templatesDirectory = 'templates'

# kreiranje direktorija za spremanje stvorenih YAML datoteka
filesDirectory = 'files'
if not os.path.exists(filesDirectory):
	os.makedirs(filesDirectory)

# kreiranje pojedinih instance.yaml datoteka
fileyaml = []
# stvaranje polja file[]
for k in range(count):
	fileyaml.append(open(filesDirectory + '/instance' + str(k + 1) + '.yaml', 'w+'))


# funkcija za kreiranje YAML datoteka za pojedinu instancu
def createInstanceYAML():
	template = open(templatesDirectory + '/instanceTemplate', 'r')

	# citanje i zapisivanje prvih 29 redova iz template-a, sve do instanceX_ip parametra
	for i in range(29):
		line = template.readline()
		for j in range(count):
			fileyaml[j].write(line)

	# zapisivanje instanceX_ip adresa
	for i in range(count):
		for j in connections[i]:
			fileyaml[i].write("  instance" + str(j + 1) + "_ip:\n    type: string\n    label: php service server\n    description: IP address of the php service " + str(j + 1) + " server.\n")
	for i in range(4):
		template.readline()

	# od resources do instanceX
	for i in range(20):
		line = template.readline()
		for j in range(count):
			fileyaml[j].write(line)

	# pisanje imena instance
	for i in range(count):
		fileyaml[i].write("  instance" + str(i + 1) + ":\n")
	template.readline()

	# citanje od imena instance do str_replace params
	for i in range(11):
		line = template.readline()
		for j in range(count):
			fileyaml[j].write(line)

	# zapisivanje service_ip parametara
	for i in range(count):
		for j in connections[i]:
			fileyaml[i].write("            __service_ip" + str(j + 1) + "__: { get_param: instance" + str(j + 1) + "_ip }\n")
	template.readline()

	# citanje i zapisivanje slijedeca 3 reda
	for i in range(3):
		line = template.readline()
		for j in range(count):
			fileyaml[j].write(line)

	for i in range(count):
		if (mysql[i]):
			fileyaml[i].write("            sudo debconf-set-selections <<< 'lamp-server^ mysql-server/root_password password grad'\n")
			fileyaml[i].write("            sudo debconf-set-selections <<< 'lamp-server^ mysql-server/root_password_again password grad'\n")
		fileyaml[i].write("            apt-get -y install lamp-server^\n")


	# citanje i zapisivanje slijedeceg reda
	line = template.readline()
	for i in range(count):
		fileyaml[i].write(line)

	# zapisivanje service_ip u file
	for i in range(count):
		fileyaml[i].write("            wget --no-check-certificate https://raw.githubusercontent.com/nikoladom91/ARIKS2016/master/Skripte/Heat/resursi/nusoap.php\n")
		for j in connections[i]:
			fileyaml[i].write("            echo \"__service_ip" + str(j + 1) + "__\" >> serviceIP.txt\n")
	template.readline()

	# zapisivanje testnih programa
	createTestProgram()

	# od wc_notify do outputs name
	for i in range(16):
		line = template.readline()
		for j in range(count):
			fileyaml[j].write(line)

	# citanje od description do kraja
	for i in range(5):
		line = template.readline()
		for j in range(count):
			fileyaml[j].write(line.replace("X", str(j + 1)))


# funkcija za kreiranje instalacijske YAML datoteke
def createInstallYAML():
	file = open(filesDirectory + '/install.yaml', 'w+')
	template = open(templatesDirectory + '/installTemplate', 'r')
	instance1 = ""
	instance2 = ""

	# citanje i zapisivanje parametara
	for i in range(64):
		line = template.readline()
		file.write(line.replace('ubuntuCloud14', image).replace('m1.small', flavor).replace('my_key1', key).replace('my_net1', private_network).replace('admin_floating_net', public_network))

	# citanje resursa
	template.readline()
	template.readline()
	for i in range(6):
		line = template.readline()
		instance1 += line
	template.readline()
	for i in range(2):
		line = template.readline()
		instance2 += line

	# zapisivanje resursa
	for i in range(count):
		file.write("  instance" + str(i + 1) + ":\n")
		file.write("    type: instance" + str(i + 1) + ".yaml\n")
		file.write(instance1)
		for j in connections[i]:
			file.write("      instance" + str(j + 1) + "_ip: { get_attr: [instance" + str(j + 1) + ", ip] }\n")
		file.write(instance2)

	file.close()


# funkcija za stvaranje testnog PHP programa na pojedinu instancu
def createTestProgram():
	# kreiranje pojedinih php datoteka
	templatePHP = open(templatesDirectory + '/phpProgramTemplate.php', 'r')

	# citanje i zapisivanje prvih 6 redova iz template-a, sve do stvaranja novog nusoap klijenta
	for i in range(6):
		line = templatePHP.readline()
		for j in range(count):
			fileyaml[j].write("            echo \"" + line[:-1] + "\" >> service" + str(j + 1) + ".php\n")

	brojac = 0
	# stvaranje nusoap klijenata
	for i in range(count):
		for j in connections[i]:
			linija = "                $service" + str(j + 1) + " = new nusoap_client(\"http://\" . $serviceIP[" + str(brojac) + "] . \"/service" + str(j + 1) + ".php?wsdl\", true);"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")
			brojac = brojac + 1
		brojac = 0

	#preskakanje jednog reda i citanje i zapisivanje slijedeceg
	line = templatePHP.readline()
	line = templatePHP.readline()
	for i in range(count):
		fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")

	# zapisivanje $result = "serviceX";
	line = templatePHP.readline()
	for i in range(count):
		line = "        $result = \"service" + str(i + 1) + "\";"
		fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")

	# citanje i zapisivanje 3 slijedeca reda
	for i in range(3):
		line = templatePHP.readline()
		for j in range(count):
			fileyaml[j].write("            echo \"" + line[:-1] + "\" >> service" + str(j + 1) + ".php\n")

	# zapisivanje $input = "serviceX";
	line = templatePHP.readline()
	for i in range(count):
		line = "$input = \"service" + str(i + 1) + "\";"
		fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")

	# citanje i zapisivanje slijedeca 3 reda iz templatePHP-a, sve do stvaranja novog nusoap klijenta
	for i in range(3):
		line = templatePHP.readline()
		for j in range(count):
			fileyaml[j].write("            echo \"" + line[:-1] + "\" >> service" + str(j + 1) + ".php\n")

	brojac = 0
	# stvaranje nusoap klijenata
	for i in range(count):
		for j in connections[i]:
			line = "        $service" + str(j + 1) + " = new nusoap_client(\"http://\" . $serviceIP[" + str(brojac) + "] . \"/service" + str(j + 1) + ".php?wsdl\", true);"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")
			brojac = brojac + 1
		brojac = 0

	#preskakanje jednog reda i citanje i zapisivanje 2 slijedeca
	line = templatePHP.readline()
	for i in range(2):
		line = templatePHP.readline()
		for j in range(count):
			fileyaml[j].write("            echo \"" + line[:-1] + "\" >> service" + str(j + 1) + ".php\n")

	# citanje i zapisivanje errora
	for i in range(count):
		for j in connections[i]:
			line = "$error" + str(j + 1) + " = $service" + str(j + 1) + "->getError();"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")
			line = "if ($error" + str(j + 1) + ") {"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")
			line = "        echo \"Constructor error: \" . $error" + str(j + 1) + " . \"\\n\";\n}\n"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")
			line = "$result" + str(j + 1) + " = $service" + str(j + 1) + "->call(\"checkService\", array(\"input\" => $input));\n"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")
			line = "if ($service" + str(j + 1) + "->fault) {"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")
			line = "        echo \"Fault: \";"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")
			line = "        print_r($result" + str(j + 1) + ");"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")
			line = "} else {"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")
			line = "        $error" + str(j + 1) + " = $service" + str(j + 1) + "->getError();"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")
			line = "        if ($error" + str(j + 1) + ") {"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")
			line = "        echo \"Error: \" . $error" + str(j + 1) + " . \"\\n\";"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")
			line = "        } else {"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")
			line = "        echo $input . \" poziva \" . $result" + str(j + 1) + " . \"\\n\";\n        }\n}\n"
			fileyaml[i].write("            echo \"" + line[:-1] + "\" >> service" + str(i + 1) + ".php\n")

	# citanje do kraja dokumenta
	for i in range(19):
		line = templatePHP.readline()
	for i in range(18):
		line = templatePHP.readline()
		for j in range(count):
			fileyaml[j].write("            echo \"" + line[:-1] + "\" >> service" + str(j + 1) + ".php\n")

createInstallYAML()
createInstanceYAML()

# zatvaranje datoteke
for l in range(count):
	fileyaml[l].close()

