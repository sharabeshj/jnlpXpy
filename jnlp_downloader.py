import argparse
import xml.etree.ElementTree as ET
import random
import string
import os
import pip

def pip_install(mod):
    pip.main(['install', mod])

if __name__ == "__main__":

    try:
        import requests
    except:
        pip_install('request')
        import requests

parser = argparse.ArgumentParser(prog='jnlp_downloader.py',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                 description='Download JAR files associated with a JNLP file and execute them'
                                 )

parser.add_argument('--link',
                    required=True,
                    help='the full URL to the JNLP file(must include http(s)://)'
                    )

args = vars(parser.parse_args())
r = ''
session = requests.Session()

randDir = ''.join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(10))

r = session.get(args['link'], verify=False)

if r.status_code is not 200:
    print('[*] Link was inaccessible, exiting.')
    exit(0)

xmltree = ''
xmlroot = ''
jnlpurl = ''

try:
    xmltree = ET.ElementTree(ET.fromstring(r.content))

except:
    print( '[*] JNLP file was misformed, exiting.')
    exit(0)

try:
    xmlroot = xmltree.getroot()
    jnlpurl = xmlroot.attrib['codebase'] + '/'

except:
    print( '[*] JNLP file was misformed, exiting.')
    exit(0)


path_delim = ''
if 'posix' in os.name:
    path_delim = '/'

else:
    path_delim = '\\'

try:
    if not os.path.exists(os.getcwd() + path_delim + randDir):
        os.mkdir(os.getcwd() + path_delim + randDir)
    else:
        print( '[*] Random directory already exists, defaulting to current.')
        randDir = '.'
except:
    print( '[*] Failed to create random directory, defaulting to current.')
    randDir = '.'

jnlpLinks = []
i = 0

for jars in xmlroot.iter('jar'):

    jnlpfile = jars.get('href').rsplit('/')[1]
    jnlppath = jars.get('href').rsplit('/')[0] + '/'
    jnlpuri = jars.get('href')

    if jars.get('version') is None:
        jnlpalt = None
        jnlpver = None
        altfile = None

    else:
        jnlpalt = jnlppath + jnlpfile.rsplit('.jar')[0] + '__V' + jars.get('version') + '.jar'
        altfile = jnlpfile.rsplit('.jar')[0] + '__V' + jars.get('version') + '.jar'
        jnlpver = jnlpuri + '?version-id=' + jars.get('version')

    jnlpLinks.append([jnlpuri, jnlpver, jnlpfile, jnlpalt, altfile])
    i+=1

for nativelibs in xmlroot.iter('nativelib'):

    jnlpfile = nativelibs.get('href').rsplit('/')[1]
    jnlppath = nativelibs.get('href').rsplit('/')[0] + '/'
    jnlpuri = nativelibs.get('href')

    if nativelibs.get('version') is None:
        jnlpalt = None
        jnlpver = None
        altfile = None

    else:
        jnlpalt = jnlppath + jnlpfile.rsplit('.jar')[0] + '__V' + nativelibs.get('version') + '.jar'
        altfile = jnlpfile.rsplit('.jar')[0] + '__V' + nativelibs.get('version') + '.jar'
        jnlpver = jnlpuri + '?version-id=' + nativelibs.get('version')


    jnlpLinks.append([jnlpuri, jnlpver, jnlpfile, jnlpalt, altfile ])
    i+=1

for link in jnlpLinks:

    print( '[+] Attempting to  download: ' + jnlpurl + link[0])
    jnlpresp = session.get(jnlpurl + link[0])

    if jnlpresp.status_code == 200:

        print( '[-] Saving file: ' + link[2] + ' to ' + randDir)
        output = open(randDir + '/' + link[2], 'wb')
        output.write(jnlpresp.content)
        output.close()

    else:

        #If the straight request didn't succeed, try to download with version info
        if link[1] is not None:

            print( '[+] Attemptinig to download: ' + jnlpurl + link[1])
            jnlpresp = session.get(jnlpurl + link[1])

            if jnlpresp.status_code == 200:
                print( '[-] Saving file: ' + link[2] + ' to ' + randDir)
                output = open(randDir + '/' + link[2], 'wb')
                output.write(jnlpresp.content)
                output.close()


        #If the straight request didn't succeed, try to download with alternative name
        if link[3] is not None and link[4] is not None:

            print( '[+] Attempting to download: ' + jnlpurl + link[3])
            jnlpresp = session.get(jnlpurl + link[3])

            if jnlpresp.status_code == 200:
                print('[-] Saving file: ' + link[4] + ' to ' + randDir)
                output = open(randDir+'/'+link[4], 'wb')
                output.write(jnlpresp.content)
                output.close()
