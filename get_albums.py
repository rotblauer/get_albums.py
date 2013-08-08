#!/usr/bin/python

import requests, re, os, shutil, json

# i have my access token in a file named access_token
# but you could also just assign it to this variable here
my_token = open("access_token", "r").read().strip()
data_path = os.path.join(os.getcwd(), 'data')
albums_path = os.path.join(os.getcwd(), 'albums')

# creating data and album directories if they don't exist
if not os.path.exists(data_path):
    os.makedirs(data_path)

if not os.path.exists(albums_path):
    os.makedirs(albums_path)

json_filename = os.path.join(data_path, "album_list.json")

if not os.path.exists(json_filename):
    # getting all album details for the token's user
    r = requests.get("https://graph.facebook.com/me/albums?access_token=%s" % my_token)

    # dropping out if we get a bad http response
    if r.status_code != 200:
        print "\nFailed to properly connect to the Facebook API."
        print "HTTP Status Code: %s\n" % r.status_code
        exit()

    # saving JSON response for the album list
    json_file = open(json_filename, "w")
    json_file.write(r.content)
    json_file.close()

    # a dict representation of albums data
    albums = r.json["data"]
else:
    json_file = open(json_filename, "r")
    albums = json.load(json_file)["data"]
    json_file.close()


# for stripping non-alphanumeric
pattern = re.compile('[\W]+')

for album in albums:
    print album['id'], album['name'].replace(' ','_')

    album_dir_name = pattern.sub('', album['name'].replace(' ','_'))
    album_path = os.path.join(albums_path, album_dir_name)

    if not os.path.exists(album_path):
        os.makedirs(album_path)

    json_filename = os.path.join(data_path, "%s.json" % album_dir_name)

    if not os.path.exists(json_filename):
        r2 = requests.get("https://graph.facebook.com/%s/photos?access_token=%s"
                          % (album['id'], my_token))
        # saving JSON response for the image list
        json_file = open(json_filename, "w")
        json_file.write(r2.content)
        json_file.close()

        images = r2.json["data"]
    else:
        json_file = open(json_filename, "r")
        images = json.load(json_file)["data"]
        json_file.close()

    icount = 0
    for image in images:
        icount += 1
        print image["source"], icount
        if image.has_key('name'):
            print image["name"]

        image_filename = os.path.join(album_path, "%s.jpg" % icount)

        if not os.path.exists(image_filename):
            r3 = requests.get(image["source"])
            image_file = open(image_filename, "wb")
            shutil.copyfileobj(r3.raw, image_file)
            image_file.close()