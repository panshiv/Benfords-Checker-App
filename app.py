from pyramid.view import view_config
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
import json
import math
import collections
import csv

@view_config(route_name='home', renderer='templates/home.jinja2')
def home(request):
     return {'title':'Application'}

@view_config(route_name="benford",renderer="json")
def benford(request):
    # get the input from form
    csv_file = request.POST['file'].file
    filename = request.POST['file'].filename 
    # check if input files is CSV or not
    name, ext = filename.split('.')
    if not ext == 'csv':
        return {"Error": "Invalid File Input! Please upload CSV file"}
    else:
        # if it is CSV
        # save in local directory uploads
        filepath = f"uploads/{filename}"
        with open(filepath,"wb") as f:
            f.write(csv_file.read())
        # Read the CSV file and extract the first digit of each number
        data = []
        reader = csv.reader(csv_file)
        for row in reader:
            try:
                num = int(row[0])
                first_digit = int(str(num)[0])
                data.append(first_digit)
            except ValueError:
                pass
        
        # Calculate the expected frequencies of each first digit according to Benford's law
        expected_freqs = [math.log10(1 + 1.0 / d) * 100 for d in range(1, 10)]
        
        # Calculate the actual frequencies of each first digit in the data
        actual_freqs = collections.Counter(data)
        total_count = sum(actual_freqs.values())
        actual_freqs = [actual_freqs[d] / total_count * 100 for d in range(1, 10)]
        
        # Check if the actual frequencies are within 5% of the expected frequencies
        for d in range(1, 10):
            expected = expected_freqs[d-1]
            actual = actual_freqs[d-1]
            if abs(expected - actual) > 5:
                message = 'Given data not follows Benford\'s law'
            else:
                # If the actual frequencies are within 5% of the expected frequencies, return a success message
                message = 'Given data satisfies Benford\'s law.'
        result =  {
            "Message": message,
            }
        json_data = json.dumps(result)
        with open(f"output/{name}.json","w") as f:
            f.write(json_data)
        return result


if __name__ == "__main__":
    with Configurator() as config:
        config.include('pyramid_jinja2')
        config.add_static_view(name='static', path='static')
        config.add_route('home', '/')
        #config.add_view(home,route_name='home')
        config.add_route('benford','/')
        # config.add_view(upload,route_name='upload')
        config.scan()
        app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 6543, app)
    server.serve_forever()