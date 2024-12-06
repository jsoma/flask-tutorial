# Building a data-driven Flask app

In this tutorial we're going to use [Flask](https://flask.palletsprojects.com/en/stable/) to build a data-driven, browseable website with [this CSV of power plants](powerplants.csv). This is a *very* bare-bones tutorial, if you want something more verbose you might check out [this old one tutorial of mine called Building Python-based, database-driven web applications (with maps!) using Flask, SQLite, SQLAlchemy and MapBox](https://jonathansoma.com/tutorials/flask-sqlalchemy-mapbox/).

## Installation

Start by installing Flask. Ignore the installation instructions on the Flask site: they're overly complicated for our quick-and-dirty tutorial.

```
pip install flask
```

Now open up a new folder in VS Code.

## Getting started

Start by creating this file and saving it as `app.py`

```py
from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
```

Then run it. The command below works because we called it `app.py`. Run this from the **command line.**

```
flask run --debug
```

## Adding URLs

Let's add another route.

```py
@app.route("/powerplants")
def powerplants():
    return "<p>This URL will have powerplants</p>"
```

Now we can visit `/powerplants`.

## Rendering full web pages

Now let's render a file instead of text.

```py
from flask import Flask, render_template

# ...remaining code...

@app.route("/powerplants")
def powerplants():
    return render_template('powerplants.html')
```

The file `powerplants.txt` will need to be inside of the `/templates/` subdirectory.

```html
<h1>This is all your powerplants</h1>
<p>Hello!</p>
```

## Getting data

We'll use pandas to draw out data from `powerplants.csv`. It isn't the best way, but it's certainly the fastest!

```py
from flask import Flask, render_template
import pandas as pd

# ...rest of the code...

@app.route("/powerplants")
def powerplants():
    # Convert the CSV to a list of dicts
    df = pd.read_csv("powerplants.csv")
    powerplants = df.to_dict('records')

    # Let's only send 20 for now
    powerplants = powerplants[:20]

    # Send the dicts to the page
    return render_template(
        'powerplants.html',
        powerplants=powerplants)
```

We'll also want to update `templates/powerplants.html` to show us the details of the power plants.

```html
<p>You have {{powerplants | length}} powerplants.</p>
```

This is a templating language called [Jinja](https://ttl255.com/jinja2-tutorial-part-1-introduction-and-variable-substitution/).

## Loops in Jinja

[Loops in Jinja](https://ttl255.com/jinja2-tutorial-part-2-loops-and-conditionals/) are pretty simple! They're kind of like normal Python loops, but... a little different.

```html
<ul>
{% for plant in powerplants %}
    <li>{{plant['Plant_Name']}}</li>
{% endfor %}
</ul>
```

Try to also add more information, like bolding the plant name and then adding the power type and state.

## Individual pages

We now want pages for each power plant.

If you look at the dataset, each power plant has a unique code - `Plant_Code`. If we think about what our URLs might look like, I think this would be a good idea:

```
/powerplants/4
/powerplants/2
...etc
```

So we'll add another route, but this one has **an integer variable in the path:**

```py
@app.route("/powerplants/<int:plant_id>")
def powerplant(plant_id):
    return f"You are looking for the plant {plant_id}"
```

Make sure your code matches mine! If you visit `/powerplants/2` it should now say "You are looking for the plant 2".

Now let's add in pandas code to find the plant with that ID.

```py
@app.route("/powerplants/<int:plant_id>")
def powerplant(plant_id):
    df = pd.read_csv("powerplants.csv")
    matching_rows = df[df['Plant_Code'] == plant_id]

    plant = matching_rows.to_dict('records')[0]

    return f"You are looking for the plant {plant}"
```

We do this in a sort of... bad way, but it works! It first finds all of the rows that match that ID, then converts them to a list and takes the first one.

## Individual page content

To populate the pages, we'll need a new template: `powerplant.html`. We'll just have it print out the power plant's name:

```html
<h1>{{plant['Plant_Name']}}</h1>
```

And then we'll adjust our function to send the plant to the plant:

```py
@app.route("/powerplants/<int:plant_id>")
def powerplant(plant_id):
    
    # ...open the CSV, get the row...

    # Send the power plant to the template
    return render_template(
        'powerplant.html',
        plant=plant
    )
```

Now when we visit `/powerplants/2` we should have a page with a nice big title on it.

## Linking our plant pages

We now need to add links to `powerplants.html` - right now it's just listing all of the power plants, but not letting you do anything with them!

Instead of just

```html
<p>Bankhead Dam</p>
```

we want it to instead say

```html
<p><a href="/powerplants/2">Bankhead Dam</a></p>
```

This just becomes a matter of fill-in-the-blanks with Jinja template variables. I find it *much* easier to start from scratch each time instead of editing something that already has variables – the curly braces just become too overwhelming!

Our final `powerplants.html` will look like this:

```html
<h1>This is all your powerplants</h1>
<p>Hello!</p>
<p>You have {{powerplants | length}} powerplants</p>
<ul>
    {% for plant in powerplants %}
    <li><a href="/powerplants/{{plant['Plant_Code']}}">{{plant['Plant_Name']}}</a></li>
    {% endfor %}
</ul>
```

## Adding a map

Back to our "show" page for a single powerplant: since we have `Latitude` and `Longitude` columns we might as well take advantage of them and add a map!

If you want to make a map, [Leaflet](https://leafletjs.com/) is a solid option. It's nothing fancy, but is one of the easiest-to-use mapping tools out there.

One the front page of the Leaflet site, there's a little bit of code that shows you how to make a map show up on a web page. The only adjustment I'm going to make to it before we add it to our page is putting opening and closing `script` tags around it.

```javascript
<script type="text/javascript">
var map = L.map('map').setView([51.505, -0.09], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

L.marker([51.5, -0.09]).addTo(map)
    .bindPopup('A pretty CSS popup.<br> Easily customizable.')
    .openPopup();
</script>
```

Even after we refresh, it won't work! That's because it requires *a few extra files*. You don't `pip install` with JavaScript and CSS, you actually request the extra files every page the page loads.

To make Leaflet work we'll need to look at the [quickstart guide](https://leafletjs.com/examples/quick-start/) and find the extra bits and pieces it wants us to add - another `script` tag, a `link` tag with some CSS, and a `div` to hold the map.

Our final html will look like this:

```html
<h1>{{plant['Plant_Name']}}</h1>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
     integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
     crossorigin=""/>

 <!-- Make sure you put this AFTER Leaflet's CSS -->
 <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
     integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
     crossorigin=""></script>

<style>
    #map { height: 300px; }
</style>

<div id="map"></div>
<script type="text/javascript">
    var map = L.map('map').setView([51.505, -0.09], 13);
    
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    L.marker([51.5, -0.09]).addTo(map)
        .bindPopup('A pretty CSS popup.<br> Easily customizable.')
        .openPopup();
</script>
```

Refresh to confirm it works.

To make the map center on our point – the dam we want to look at – we just need to tweak the two spots that point out the coordinates.

```js
// Before
[51.505, -0.09]
// After
[{{plant['Longitude']}}, {{plant['Latitude']}}]
```

One problem is **VS Code isn't very happy with Jinja templates**. It's going to do a lot of underlining and such when you do this. It's okay, though, as long as you've cut and pasted (or written your code) perfectly it will work out okay.

And if it *doesn't work?* Just undo until it works again, then try again.

While we're at it, we can also add the power plant name to the popup:

```js
// Before
.bindPopup('A pretty CSS popup.<br> Easily customizable.')
// After
.bindPopup('Power plant name: <strong>{{plant['Plant_Name']}}</strong>')
```

### Adding "slice" pages based on a column

Beyond overall "list" pages and individual "show" pages, you can display slices of your data. For example, we could look at all of the power plants in a single state

```py
@app.route("/states/<str:state_name>")
def by_state(state_name):
    # Open the CSV and filter
    df = pd.read_csv("powerplants.csv")
    matching_rows = df[df['StateName'] == state_name]

    # Convert to a list of dicts
    powerplants = matching_rows.to_dict('records')

    # Send all of the power plants to a new template
    # also send the state name!
    return render_template(
        'state.html',
        state_name=state_name,
        powerplants=powerplants
    )
```

And the `state.html` file:

```html
<h1>{{state_name}}</h1>
<p>There are {{powerplants | length }} powerplants in {{state_name}}</p>

<h2>Map of power plants in this state</h2>

<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
 <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<style>
    #map { height: 300px; }
</style>

<div id="map"></div>

<script type="text/javascript">
    var map = L.map('map');
    const bounds = L.latLngBounds([]);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    {% for plant in powerplants %}
        marker = L.marker([{{plant['Latitude']}}, {{plant['Longitude']}}]).addTo(map)
            .bindPopup('{{plant['Plant_Name']}}')

        bounds.extend(marker.getLatLng());
    {% endfor %}

    map.fitBounds(bounds, { padding: [30, 30]});
</script>
```

## Pagination

Now let's head back to a listing page: **we need to display more than just twenty elements.

We're going to adjust things so we can access more powerplants through the URL, like `/powerplants?page=3`.

To access that parameter from Flask, we need to add another import:

```py
from flask import Flask, render_template, request
```

Now let's add some code inside of `/powerplants`. Previously we just took the first twenty. Now we'll look at the current page in the URL and just based on that. If it's 20 per page, on page 3, we'll start on 20 * 3 = 60, and end with 60 + 20 = 80.

```py
# Before
# powerplants = powerplants[:20]

# After
PER_PAGE = 20
current_page = int(request.args.get('page', 1))
start = PER_PAGE * current_page - PER_PAGE
end = PER_PAGE * current_page

powerplants = powerplants[start:end]
```

If you refresh and just the URL with `?page=3`, `?page=4`, etc, you'll be able to see different batches of power plants.

Next up we need to **add the pagination links**. We can do this by using the [flask-paginate](https://pythonhosted.org/Flask-paginate/) package. Start by installing it:

```
pip install flask-paginate
```

To use it, we need to make two adjustments, **one inside of the route and the other inside of the HTML**.

Inside of the route, we'll add two pieces: first we'll build a `pagination` object and secondly we'll send the `pagination` object to the template.

```py
pagination = Pagination(total=df.shape[0],
                        page=current_page,
                        per_page=PER_PAGE)


# Send the dicts to the page
return render_template(
    'powerplants.html',
    powerplants=powerplants,
    pagination=pagination
)
```

The `Pagination` object takes the total amount of rows in the dataframe, the current page, and the number per page, packaging it all up. If we were using a database we could be fancier with it, but since we aren't... we won't!

To actually show the results on the HTML page, we now adjust `powerplants.html` to render the links:

```py
{{ pagination.link }}
```

And if you want to make it look nice? Add some CSS! You can just drop it down into the bottom of the HTML file.

```html
<style>
.pagination {
  display: flex;
  list-style: none;
  padding: 0;
  margin: 20px 0;
  justify-content: center;
}

.page-item {
  margin: 0 5px;
}

.page-link {
  display: block;
  padding: 10px 15px;
  text-decoration: none;
  border: 1px solid #dee2e6;
  background-color: #fff;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.page-link:hover {
  background-color: #f0f0f0;
}

.page-item.active .page-link {
  background-color: #007bff;
  color: #fff;
  border-color: #007bff;
}

.page-item.disabled .page-link {
  color: #6c757d;
  pointer-events: none;
  background-color: #e9ecef;
  border-color: #dee2e6;
}

/* Adjustments for small screens */
@media (max-width: 576px) {
  .pagination {
    flex-wrap: wrap;
  }

  .page-item {
    margin: 3px;
  }

  .page-link {
    padding: 8px 12px;
    font-size: 0.9rem;
  }
}

</style>
```

If you also have URLs that are based on other filters, you should be able to re-use all of the code for them as well.

## There you go!

There's a *lot* you can do from here, but that is the basics of how to get a database-driven Flask site up and running.