import folium
import json
from shapely.geometry import shape, Point
from bs4 import BeautifulSoup
from folium.plugins import LocateControl, MarkerCluster
from Dictionary_of_Pubs import pubs_visited

# To choose a map tile style, either choose from in-built defaults or go to http://leaflet-extras.github.io/leaflet-providers/preview/
# to find a style and its URL tile-server. For example the Stadia style is good.
# The final option is to use Mapbox. Create a new map style online and you can even customize it to your own taste.
# After map is published, go to 'Share & Develop' -> 'Third Party' -> 'Fulcrum' and use copy link into tiles= argument. Remember to attribute the map correctly.
# Mapbox ask to include this attribute too, but I'm leaving it out at the moment because it takes up too much space. <strong><a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a></strong>

# Create the map. Location is the centre of map.
OxfordshireMap = folium.Map(location=[51.7831, -1.3065], tiles='https://tiles.stadiamaps.com/tiles/osm_bright/{z}/{x}/{y}{r}.png', attr='&copy; <a href="https://stadiamaps.com/">Stadia Maps</a>, &copy; <a href="https://openmaptiles.org/">OpenMapTiles</a> &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors', zoom_start=9, max_zoom=19, control_scale=True)  # width=50%,

# Define county boundary and shading style
border_style = {'color': '#000000', 'weight': '1.5', 'fillColor': '#58b5d1', 'fillOpacity': 0.08}
# A good blue has code: 58b5d1.

# Create Oxfordshire boundary and add to map
boundary = folium.GeoJson(open('./Images/Oxfordshire_Boundary.geojson').read(), name='Oxfordshire Boundary', style_function= lambda x: border_style, overlay=False)
boundary.add_to(OxfordshireMap)

# Create custom beer glass icon
beerGlass_img = './Images/Pubs of Oxfordshire Icon Transparent Outlined.png'

# Load in Oxford City Boundary to help define cluster of Oxford pubs
with open('./Images/Oxford City Boundary.json', 'r') as file:
    oxford_json = json.load(file)
oxford_boundary = shape(oxford_json['features'][0]['geometry'])

# Create marker cluster that will contain pubs within Oxford.
oxford_cluster = MarkerCluster(options={'showCoverageOnHover': False,
                                        'zoomToBoundsOnClick': True,
                                        'spiderfyOnMaxZoom': False,
                                        'disableClusteringAtZoom': 13})

# Create marker for each pub in pub dictionary
for pub, details in pubs_visited.items():
    # Define marker variables
    name = pub
    coordinates = details[0]
    insta_post = details[1]
    website = details[2]
    directions = details[3]

    # Create custom icon with beer glass
    custom_icon = folium.CustomIcon(beerGlass_img, icon_size=(35, 35), popup_anchor=(0, -22))
    # Define html inside marker pop-up
    pub_html = folium.Html(f"""<p style="text-align: center;"><b><span style="font-family: Didot, serif; font-size: 18px;">{name}</b></span></p>
    <p style="text-align: center;"><iframe src={insta_post}embed width="220" height="270" frameborder="0" scrolling="auto" allowtransparency="true"></iframe>
    <p style="text-align: center;"><a href={website} target="_blank" title="{name} Website"><span style="font-family: Didot, serif; font-size: 14px;">{name} Website</span></a></p>
    <p style="text-align: center;"><a href={directions} target="_blank" title="Directions to {name}"><span style="font-family: Didot, serif; font-size: 14px;">Directions to {name}</span></a></p>
    """, script=True)

    # Create pop-up with html content
    popup = folium.Popup(pub_html, max_width=220)
    # Create marker using instance of custom_icon and popup.
    custom_marker = folium.Marker(location=coordinates, icon=custom_icon, tooltip=name, popup=popup)
    # If pub is within Oxford boundary, add to Oxford cluster
    if oxford_boundary.contains(Point((coordinates[1], coordinates[0]))):
        custom_marker.add_to(oxford_cluster)
    else:
        # Else add marker to map
        custom_marker.add_to(OxfordshireMap)

# Add oxford cluster to map
oxford_cluster.add_to(OxfordshireMap)

# Add geolocation feature to map.
LocateControl(auto_start=False).add_to(OxfordshireMap)

# Define webpage title html and add to script.
tab_title = """<title>Pubs of Oxfordshire Maps</title>"""
OxfordshireMap.get_root().html.add_child(folium.Element(tab_title))

# Save map to HTML
OxfordshireMap.save('Map.html')

# Define tab icon html (using https://realfavicongenerator.net/ which generates favicons). Images must be in the ROOT folder.
# Apple iOS truncates App names with > 12 chars. So we use Figure Space char (&#x2007;) to still get a space
tab_icon = """<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
<link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
<link rel="icon" type="image/png" sizes="16x16" href="favicon-16x16.png">
<link rel="manifest" href="site.webmanifest">
<link rel="mask-icon" href="safari-pinned-tab.svg" color="#484848">
<meta name="msapplication-TileColor" content="#535353">
<meta name="theme-color" content="#ffffff">
<meta name="apple-mobile-web-app-title" content="Pubs &#x2007; of &#x2007; Oxfordshire">
<meta http-equiv="content-type" content="text/html; charset=UTF-8" />"""
# Pass map HTML text to bs4, returns a soup object.
soup = BeautifulSoup(open('Map.html'), 'html.parser')
# Find head section and append the 'tab_icon" html. Favicon links must be in the <head> section.
head = soup.find('head')
head.append(BeautifulSoup(tab_icon, 'html.parser'))  # Needs to be parsed as html by bs4 to work.
# Overwrite the edited html to the Map.html file
with open('Map.html', 'w') as html_file:
    html_file.write(str(soup))