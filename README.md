mako-mori
=========

### What

An experimental scalable and load balanced cluster (with caveats) :smile: It's an HTTP-serving app that forwards requests to the nearest slave server (and if necessary, provision the slave server dynamically).

*Disclaimer: treat this as a weekend hack project (don't put it in production).*

It's a Google App Engine application (HTTP) backed by Amazon Web Services. It acts as a reverse proxy and a manager for AWS EC2 computers (instances). When it receives an HTTP request:

- It gets the latitude and longitude of the request.
- It computes the geo distance and finds the nearest [AWS region](http://aws.amazon.com/about-aws/globalinfrastructure/).
- If the region has an active instance, it forwards the request to it.
- If not, it provisions an instance dynamically.

### Example

The app has two endpoints `GET /status` and `GET /test`. For example (with pretty print JSON):

    $ curl -s https://localhost/status | python -m json.tool 
    {
    "result": [
        {
            "city": "Northern California",
            "name": "us-west-1",
            "pending": 0,
            "running": 0
        },
        {
            "city": "Northern Virginia",
            "name": "us-east-1",
            "pending": 0,
            "running": 0
        },
        {
            "city": "Oregon",
            "name": "us-west-2",
            "pending": 0,
            "running": 0
        },
        {
            "city": "Sao Paulo",
            "name": "sa-east-1",
            "pending": 0,
            "running": 0
        },
        {
            "city": "Ireland",
            "name": "eu-west-1",
            "pending": 0,
            "running": 0
        },
        {
            "city": "Singapore",
            "name": "ap-southeast-1",
            "pending": 0,
            "running": 0
        },
        {
            "city": "Sydney",
            "name": "ap-southeast-2",
            "pending": 0,
            "running": 0
        },
        {
            "city": "Tokyo",
            "name": "ap-northeast-1",
            "pending": 0,
            "running": 0
        }
    ],
    "status": "OK"
    }

It lists the number of running and pending (booting up) instances in each region. As you can see, we have 0 running instances. Thus, we do:

    $ curl https://localhost/test
    {"status":"STARTING"}

After a few seconds:

    $ curl https://localhost/test
    {"status":"PENDING"}

After a minute or so:

    $ curl https://localhost/test
    {"status":"OK","region":"Sydney","result":"ip-172-31-14-19\nap-southeast-2\n"}

It gives the output of a static file located on the instance (closest to where the request comes from).

The instance is configured to shutdown after 45 minutes.

### Things to do

Several things that can be done:

- Put the AWS Elastic Load Balancer in front of the instances.
- Use the AWS Route53 for a true latency based routing.
- Compartmentalize the process using Docker (for process isolation and added security).
- Use software configuration management.
