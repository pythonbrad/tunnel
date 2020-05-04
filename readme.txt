This program create a tunnel to communicate with a siteweb A via a siteweb B.
client<->remote_client<->siteweb_A<->getter<->remote_getter<->siteweb_B

But for this test version, the getter is also the siteweb_A

# HOW TO USE
install a django version >= 2

# To python, do any modification
# you can use the hexdump function with python2 only
python client.py

# In the tunnel folder
python manage.py migrate
python manage.py runserver