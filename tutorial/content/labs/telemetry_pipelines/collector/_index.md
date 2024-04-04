---
title: "Collector"
draft: false
weight: 1
---

### Why do we need Collectors?

Over the previous labs, we have seen how OpenTelemetry's SDK implements the instrumentation which produces the telemetry data.
We also configured a basic pipeline to export the generated telemetry directly from the SDK.
The *Collector* is a key component of OpenTelemetry to manage how telemetry is processed and forwarded.
At this point you might ask yourself: How are these capabilities different from the SDK?
With the SDK, the telemetry pipeline was defined *in* the application code.
Depending on your use-case, this approach can be perfectly fine.
A Collector, on the other hand, is a binary written in Go, that runs as a separate, standalone process.
Its provides flexible, configurable and vendor-agnostic system to process telemetry *outside* the application.
It essentially serves as a broker between a telemetry source and the backend storing the data.

Deploying a Collector has many advantages.
Most importantly, it allows for a cleaner separation of concerns.
Developers shouldn't have to care about what happens to telemetry after it has been generated. 
With a collector, operators are able to control the telemetry configuration without having to modify the application code.
Additionally, consolidating these concerns in a central location streamlines maintaince.
In a SDK-based approach, the configuration of where telemetry is going, what format it needs to be in, and it should be processed is spread across various codebases managed by separate teams.
However, telemetry pipelines are rarely specific to individual applications.
Without a collector, making adjustments to the configuration and keeping it consistent across applications can get fairly difficult.
Moving things out of the SDK has other benefits.
For instance, the overal configuration of the SDK becomes much leaner.
Moreover, we no longer have to re-deploy the application everytime we make a change to the telemetry pipeline.
Troubleshooting becomes significantly easier, since there is only a single location to monitor when debugging problems related to telemetry processing.
Offloading processing and forwarding to another process means applications can spend their resources on performing actual work, rather than dealing with telemetry.
Before going into more detail, let's look at the components that make up a collector.

### architecture of a collector pipeline
{{< figure src="images/collector_arch.drawio.svg" width=600 caption="collector to process and forward telemetry" >}}

The pipeline for a telemetry signal consists of a combination of receivers, processors, and exporters.


A **receiver** is how data gets from a source (i.e. the application) to the OpenTelemetry collector.
This mechanism can either be pull- or push-based.
Out-of-the-box, the Collector supports an [OTLPReceiver](https://github.com/open-telemetry/opentelemetry-collector/tree/main/receiver/otlpreceiver) for receiving traces, metrics and logs in OpenTelemetry's native format
The [collector-contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver) repository includes a range of receivers to ingest telemetry data encoded in various protocols.
For example, there is a [ZipkinReceiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/zipkinreceiver) for traces, [StatsdReceiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/statsdreceiver) and [PrometheusReceiver](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/receiver/prometheusreceiver) and much more.
Once data has been imported, receivers convert telemetry into an internal representation.
Then, receivers pass the collected telemetry to a chain of processors.

A **processor** provides a mechanism to pre-process telemetry before sending it to a backend.
There are two categories of processors, some apply to all signals, while others are specific to a particular type of telemetry.
Broadly speaking processing telemetry is generally motivated by:
- to improve the data quality
  - add, delete, rename, transform attributes
  - create new telemetry based on existing data
  - convert older version of a data source into one that matches the current dashboards and queries used by the backend
- for governance and compliance reasons
  - use attributes to route data to specific backends
- to reduce cost
  - drop unwanted telemetry via allow and deny lists
  - tail-based sampling
- security
  - scrubbing data to prevent sensitive information from being stored (and potentially leaked) in a backend
- influence how data flows through the pipeline
  - batch 
  - retry
  - memory limit

By connecting processors into a sequential hierarchy, we can process telemetry in complex ways.
Since data is passed from one processor to the next, the order in which processors are specified matters.

Finally, the last processor in a chain hands its output to an **exporter**.
The exporter takes the data, converts the internal representation into a protocol of choice, and forwards it to one (or more) destination.
Similar to receivers, the collector ships with built-in exporters for [OTLP](https://github.com/open-telemetry/opentelemetry-collector/tree/main/exporter).
As previously mentioned, many open-source or commercial observability backends are built around custom data formats.
Even though OpenTelemetry is becoming more popular, your current backend might not yet (or is in the early stages) support OTLP.
To solve this, the [collector-contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter) repository includes exporters for many telemetry protocols.

<!-- configuration -->
{{< figure src="images/collector_config.drawio.svg" width=600 caption="YAML configuration" >}}

Now, let's look at how to configure the collector.
As with most cloud-native deployments, we express configuration via a YAML format.
It has three main sections to *define* the `receivers`, `processors`, `exporters`  components that we'll use to build our telemetry pipelines.
At the top level, each component has an ID that consists of the type (and optionally name).
The ID serves as a unique reference to the component.
Beneath that, a set of (type dependent) fields configure the component.

The `pipelines` section at the bottom of the file defines the pipelines within the collector.
Each pipeline is identified by a unique ID that specifies the type of telemetry data and (optionally) name.
Below that, the `receiver`, `processor`, and `exporter` fields outline the structure of the data flow with the pipeline.
Each field contains a list of references to component IDs.
If a pipeline has more than one receiver, the data streams will get merged before being fed to the sequence of processors.
If there are multiple exporters, the data stream will be copied to both.
It is also possible for receivers and exporters to be shared by pipelines.
If the same receiver is used in different pipelines, each pipeline receives a replica of the data stream.
If different pipelines target the same exporter, the data stream will be merged into one.

### define a basic collector pipeline

Let's put the knowledge into practice.
Open the compose.yml file to review the lab environment.
It includes two services instrumented with OpenTelemetry, an instance of the OpenTelemetry Collector, and telemetry backends such as Prometheus for metrics storage, Jaeger All-in-one for span storage and analysis, and a Grafana frontend for visualizing metrics.


```yaml { title="docker-compose" }
otel-collector:
  image: otel/opentelemetry-collector-contrib
  volumes:
    - ./otel-collector-config.yaml:/etc/otelcol-contrib/config.yaml
  ports:
    - 4317:4317
    - 4318:4318
```

A successful deployment consists of three things.
First, we deploy a Collector for which there are several strategies.
We'll examine them later.
For now, let's focus on the `otelcol` section in `compose.yml`.
The collector exposes a set of network ports to which services can push their telemetry.
Besides that, we also mount a YAML file within the Collector's container.
It contains the configuration of Collector's components and pipelines.

```yaml { title="compose.yaml" }
  java-app:
    image: ${JAVA_SVC_NAME}:0.1
    container_name: ${JAVA_SVC_NAME}
    build:
      context: ./java-app
      dockerfile: ./deployment/docker/app.Dockerfile
    restart: unless-stopped
    ports:
      - "${JAVA_SVC_PORT}:${JAVA_SVC_PORT}"
    environment:
      - OTEL_METRICS_EXPORTER=__MISSING__
      - OTEL_TRACES_EXPORTER=__MISSING__
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://__MISSING__:__MISSING__
    depends_on:
      - otelcol
      - postgres-petservice
```

Before we can receive telemetry, we must first ensure that the SDK of instrumented services send their telemetry to the collector. 
In the case of our Java application, the agent [automatically](https://github.com/open-telemetry/opentelemetry-java/tree/main/sdk-extensions/autoconfigure) picks up configuration from environment variables.
Try to fill in the gaps in the `environment` of the `java-app`.
The Java service should serve its metrics via a Prometheus endpoint and send spans to the collector using OTLP.
Save your changes.
Create a new `config.yaml` file in the `./otelcollector` directory. 
Here, we'll sketch out a basic Collector pipeline that connects telemetry sources with their destinations.
It declares pipelines components (receiver, processor, exporter), specifies telemetry pipelines and their data flow.

```yaml { title="config.yaml" }
receivers: 
  otlp:  # logs, metrics, traces in native format (push)
    protocols:
      grpc:
        endpoint: "0.0.0.0:__MISSING__"

  prometheus: # scrape metrics endpoints (pull)
    config:
      global:
        scrape_interval: 15s # Adjust this interval as needed
      scrape_configs:
        - job_name: 'flask'
          static_configs:
            - targets: ['127.0.0.1:5000'] # Adjust the Prometheus address and por
```

Start by creating an OTLP Receiver that listens for logs, metrics, and traces on a host port. 
Although OpenTelemetry is becoming widely adopted, applications maz prefer to export telemetry in a non-native format (such as Prometheus, Zipkin, Jaeger, and more).
Since our Java application serves metrics as a Prometheus endpoint, let's add a receiver to the collector to scrape it at regular intervals.

```yaml
processors:
  batch:
```

Processors are a powerful tool that let us shape telemetry in arbitrary ways.
Since this excercise focuses on ingest rather than on processing, we'll keep this part as simple as possible.
While it is possible to define pipelines without any processors, it is recommended to at least configure a [`batch processor`](https://github.com/open-telemetry/opentelemetry-collector/tree/main/processor/batchprocessor).
Buffering and flushing captured telemetry in batches means that the collector can significantly reduce the number of outgoing connections.

```yaml
exporters:
  otlphttp/prometheus:
    endpoint: "http://prometheus:9090/api/v1/otlp" 
    tls:
      insecure: true

  otlp/jaeger:
    endpoint: "jaeger:4317"
    tls:
      insecure: true
```

With processors in place, move on to define exporters to forward telemetry to our backends.
Telemetry backends typicall offer multiple ways to ingest telemetry for wide compatability.
For Prometheus, one option is to use a [Prometheus Exporter](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/exporter/prometheusexporter).
The collector exports and exposes metrics via an HTTP endpoint that can be scraped by the Prometheus server.
While this aligns with Prometheus a pull-based approach, another option is to use a feature flag to enable native OpenTelemetry support.
In this case, Prometheus serves an HTTP route `/otlp/v1/metrics` to which services push metrics via OTLP.
This approach is similar to the jaeger-collector (included in the jaeger-all-in-one binary), which exposes a set of ports to receive spans in different formats.
Add a [OTLP HTTP Exporter](https://github.com/open-telemetry/opentelemetry-collector/tree/main/exporter/otlphttpexporter) to write metrics to Prometheus and a [OTLP gRPC Exporter](https://github.com/open-telemetry/opentelemetry-collector/tree/main/exporter/otlpexporter) to ingest traces into Jaeger.
For simplicity, we'll set the `tls` property to insecure.
A production deployment should supply certificates to encrypt the communication between the collector and the backend.

```yaml
# configure the data flow for pipelines
service:
  pipelines:
    metrics/example:
      receivers: [otlp, prometheus]
      processors: [batch]
      exporters: [otlphttp/prometheus]
    traces/example:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/jaeger, debug]
```

After declaring the components, we can finally combine them to form telemetry pipelines.
For a
A valid pipeline requires at least one receiver and exporter.
In addition, all components must support the data type specified by the pipeline.
Note that a component may support one *or* more data types.
For instance, we've defined a single OTLP Receiver for logs, metrics, and traces.
Placing these components in a pipeline, provides the necessary contex for how they are used.
If we add a OTLP Receiver to a traces pipeline, its role is to receive spans.
Conversely, a Prometheus receiver is inherently limited to metrics data
Therefore, it can only be placed in a corresponding pipeline.
Now, let's define the dataflow for the `traces/example` and `metrics/example` pipelines.
Add the references to the relevant components in the receivers, processors, and exporters lists.

```
docker compose
```
To confirm that everything works as expected, let's deploy the environment.
You should be able to access the observability services using the following URLs:
You can reach the backends using
- [Grafana UI](localhost:3000)
- [Jaeger UI](http://localhost:16686/)
- [Prometheus Web](localhost:9090)


<!-- We'll set up receivers and exporters all-in-one


- configure the collector pipeline
  - receive telemetry
    - by listening for telemetry on exposed endpoints
    - scraping targets
  - to process telemetry
  - to connect collector with backends
    - collector pushes telemetry to backends
    - backends pull telemetry from the collector

 -->

### different ways to deploy a collector

To test whether the pipeline works as expected, we must deploy a collector.
Before we do that, let's look at different Collector topologies.
A collector can run as a sidecar, node agent, or standalone service.

<!-- sidecar -->
{{< figure src="images/collector.drawio_sidecar.svg" width=400 caption="placeholder" >}}

In a **sidecar-based** deployment, the collector runs as a container next to the application.
Having a collection point to offload telemetry as quickly as possible has several advantages.
By sharing a pod, the application and collector can communicate via localhost.
This provides a consistent destination for the application to send its telemetry to.
Since local communication is fast and reliable, the application won't be affected by latency that might occur during telemetry transmission. 
This ensures that the application can spend its resources processing workloads instead of being burdened by the telemetry collection, processing, and transmission.

<!-- local agent -->
{{< figure src="images/collector.drawio_agent.svg" width=400 caption="placeholder" >}}

Another option is to run a collector **agent** on every node in the cluster.
In this case, the collector serves as a collection point for all applications running on a particular node.
Similar to sidecars, applications can evacuate the produced telemetry quickly.
However, having a single agent per node means that we decrease the number of connections to send telemetry.
Furthermore, a node agent provides a great place to augment the telemetry generated by the SDK.
For example, an agent can collect system-level telemetry about the host running the workloads, because it isn't isolated by a container.
It also allows us to enrich telemetry with resource attributes to describe where telemetry originates from.


<!-- standalone service -->
{{< figure src="images/collector.drawio_service.svg" width=400 caption="placeholder" >}}

Finally, there is the option to run the collector as a dedicated **service** in the cluster.
It is no surprise that processing telemetry consumes memory resources and CPU cycles.
Since pod or node collectors run on the same physical machine, these resources are no longer available to applications.
Moreover, the capacity of the telemetry pipeline is tightly coupled to the number of pods or agents/nodes. 
Certain conditions will cause applications to produce large volumes of telemetry. 
If a local collector lacks the resources to buffer, process, and ship telemetry faster than it is produced, data will be dropped. 
A horizontally scalable collector service lets us deal with low and high-tide telemetry scenarios more efficiently and robustly.
Having a load balancer in front of a pool of collectors allows us to scale resources based on demand.
Even distribution also reduces the risk that a single collector gets overwhelmed by a spike in telemetry.
By running collectors on a dedicated set of machines, we no longer compete with applications for available resources.

- network means latency
- can connect several tiers of Collector deployments configured to perform specialized processing tasks

### 1.2 deploy a collector


<!-- Notes
- vendor-agnostic implementation of how to receive, process and export telemetry data
- scalable
- supports popular observability data formats
- can send to one or more open source or commercial back-ends
- local Collector agent is the default location to which instrumentation libraries export their telemetry data.
- allows your service to offload data quickly and the collector can take care of additional handling like retries, batching, encryption or even sensitive data filtering. 
-->
