---
title: "Integrated Usage Scenario"
draft: false
weight: 3
---

## Intro

This introductory lab exercise will demonstrate capabilities of OpenTelemetry from a plain end-user perspective. There will be no changes in configuration necessary. It's simply about starting a set of pre-defined containers and walk through usage scenarios.

The intention is to provide a high-level understanding how OpenTelemetry works, how it integrates with both application components and observability tools and become familiar with a typical setup.

It furthermore provides a lookout to the various chapters of this lab.

## Architecture

The following diagram explains the architecture:

-- TODO: DIAGRAM IN HERE --

- there is an simple underlying polylot, multi-service application
  - the components are implemented in Java (Spring Boot) and Python (Flask)
  - two alternate frontend connect to a backend part, which in turn connects to a Postgres database
  - there is a simple load-generator, which continuesly sends load to the frontend components

- the application components are already instrumented by an OpenTelemetry agent

- all of the collected information is being sent to an OpenTelemetry collector

- the OpenTelemetry Collector exports the information to various thirs-party applications
  - the (distributed) traces are exported to a Jaeger instance
  - the metrics are exported to a Prometheus instance (Grafana?)
  - the logs are exported to an OpenSearch instance? 

The entire stack of components is modeled in containers and can be run using a docker-compose file.

## Demo environment

To access the demo environment switch to the directory for this exercise:

```sh { title="terminal" }
cd /workspace/exercise-use-case-scenario
```

Then execute the docker-compose file to build and bring up the containers.

```sh { title="terminal" }
docker compose up
```

The output should show the startup process of the containers and all standard out and standard error output of the running containers afterwards.


The beginning of the output should look similar to this:
```
[+] Running 8/0
 ✔ Container python-java-otel-todolist-todoui-thymeleaf-1        Created                                                                                     0.0s 
 ✔ Container python-java-otel-todolist-postgresdb-1              Created                                                                                     0.0s 
 ✔ Container python-java-otel-todolist-loadgenerator-1           Created                                                                                     0.0s 
 ✔ Container python-java-otel-todolist-jaeger-1                  Created                                                                                     0.0s 
 ✔ Container python-java-otel-todolist-prometheus-1              Created                                                                                     0.0s 
 ✔ Container python-java-otel-todolist-todoui-flask-1            Created                                                                                     0.0s 
 ✔ Container python-java-otel-todolist-todobackend-springboot-1  Created                                                                                     0.0s 
 ✔ Container python-java-otel-todolist-otelcol-1                 Created 
```

As the ongoing output of all components can get very noisy, it is recommended to start a new terminal sessionand leave the 'docker compose up' terminal session running in the background.

It will take up to two minutes on a standard machine until all containers are in a ready state.

Validate the running behaviour by executing:

```sh { title="terminal command" }
docker ps
```

You should see 8 running containers

``` { title="output" }
Name: python-java-otel-todolist-todobackend-springboot-1		Uptime: 3 minutes ago	Ports: 0.0.0.0:8080->8080/tcp
Name: python-java-otel-todolist-otelcol-1		Uptime: 3 minutes ago	Ports: 0.0.0.0:4317-4318->4317-4318/tcp, 55678-55679/tcp
Name: python-java-otel-todolist-postgresdb-1		Uptime: 3 minutes ago	Ports: 0.0.0.0:5432->5432/tcp
Name: python-java-otel-todolist-todoui-thymeleaf-1		Uptime: 3 minutes ago	Ports: 0.0.0.0:8090->8090/tcp
Name: python-java-otel-todolist-prometheus-1		Uptime: 3 minutes ago	Ports: 0.0.0.0:9090->9090/tcp
Name: python-java-otel-todolist-jaeger-1		Uptime: 3 minutes ago	Ports: 5775/udp, 5778/tcp, 14250/tcp, 6831-6832/udp, 14268/tcp, 0.0.0.0:16686->16686/tcp
Name: python-java-otel-todolist-todoui-flask-1		Uptime: 3 minutes ago	Ports: 0.0.0.0:5001->5000/tcp
Name: python-java-otel-todolist-loadgenerator-1		Uptime: 3 minutes ago	Ports:
```

## Accessing the demo application components

As you could see in the results of the `docker ps` call in the previous exercise most application components expose their service over a certain port.

Via those ports it is possible to access the various exposed UIs.

If you run your application with a local container daemon, simply access them via `localhost`. If you are using a cloud-based setup like Codespaces or Gitpod , please see the section "How to use this lab".

-- TODO: Build this section :-) --

E.g. the web UIs of the Python and Java frontend can be accessed like

- [Python frontend](http://localhost:5001)
- [Java frontend](http://localhost:8090)

The core part of the application exposes a REST API and can also be accessed via URL

- [Java frontend](http://localhost:8080/todos/)

However it's of course more convenient (and better for showing distributed traces) when invoking the app through the web UIs.

You can of course feel free to add some "ToDo" items yourself and/or set some of them done. Most likely you will also see an item called "Sample" come and go. This is being set and removed by the load generator.

## Configuration and data flow

The docker-compose file itself already reveals a lot about the configuration of the components.

If you look into it under the part services, you will see that both Java components and the Python app have an environment property called `OTEL_RESOURCE_ATTRIBUTES=service,name` and each of them has it set to an own value:

```yaml { title="backend-springboot" }
    environment:
      - OTEL_RESOURCE_ATTRIBUTES=service.name=todobackend-springboot
```

```yaml { title="frontend-flask" }
    environment:
      - OTEL_RESOURCE_ATTRIBUTES=service.name=frontend-flask
```

```yaml { title="frontend-thymeleaf" }
    environment:
      - OTEL_RESOURCE_ATTRIBUTES=service.name=frontend-thymeleaf
```

This is the property how the components identify themself within the OpenTelemetry scope. The name will appear later again in various dashboards.

More details about how to configure application components automatically or manually, see the later chapter "Instrumentation".

Furthermore there is a property, which they all share:

```yaml { title="shared config" }
    environment:
      - OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT}
```

whereas the actual value of this endpoint is specified in an `.env`file:

```env { title=".env" }
OTEL_COLLECTOR_HOST=otelcol
OTEL_COLLECTOR_PORT_GRPC=4317
OTEL_COLLECTOR_PORT_HTTP=4318
OTEL_EXPORTER_OTLP_ENDPOINT=http://${OTEL_COLLECTOR_HOST}:${OTEL_COLLECTOR_PORT_GRPC}
```

This shows that all components point to the OpenTelemetry collector and use the listening GRPC port 4317.
The chapter "Collector" will provide more details on how to configure the OpenTelemetry collector.

# Tracing

OpenTelemetry allows to export the tracing information to various third-party applications. A popular Open-Source option is a tool called [Jaeger Tracing](https://jaegertracing.io)

The collector in this environment is configured to export the tracing metrics to the Jaeger instance.

You can access the Jaeger web UI on the following [link](http://localhost:16686)

After opening the click you will be redirected to the Search page of Jaeger. Initially there is no trace information displayed. You need to query first.

The page you should be seeing looks like this:

{{< figure src="images/jaeger_main.png" width=700 caption="Jaeger main screen" >}}

On the top left corner there is a drop down list called "Services". If you expand it, it will show all services Jaeger has tracing information of.

{{< figure src="images/jaeger_services_selection.png" width=300 caption="Jaeger services selection" >}}

It will show the various services that are currently running in the sample application. Pick the "todobackend-springboot" one and it will navigate to a page where the recently collected traces are being listed.

{{< figure src="images/jaeger_traces_recent.png" width=700 caption="Jaeger recent traces" >}}

The diagram on top displays a distribution of collected traces over the last minutes indicating the amount of invocations with the size of the dot as well as duration on the y-axis.

As the timestamps and duration times vary your screen will look certainly look a bit different from the results being displayed in the screenshots here.

You can alter the query parameters on the "Search" panel on the left, but since data collection has just started only the short-term results are most likely meaningful.

On the list of traces identify one which is called `todoui-flask: /add`

{{< figure src="images/jaeger_trace_selection.png" width=700 caption="Individual trace" >}}

You can see it is a composite of an invocation using both Python and Java components.

Click on it for further analysis. It will take you to the following screen:

{{< figure src="images/jaeger_trace_todoui_flask.png" width=700 caption="Individual trace" >}}

This shows the break down of duration times. The outer boundary is the overall trace, each part of it no matter of the nesting level is called a span. The different application components are highlighted in different colours, so it is easy to spot which part of the overall time was used by the backend component.

There are various ways to interact with this graph. You will see arrows to colapse/expand individual or all sections. If you hover over individual parts, more details are revealed. If you click on a certain span it will expand a detail view. Pick the 2nd one in the hierarchy, which is called `todoui-flask POST`.

{{< figure src="images/jaeger_traces_todoui_flask_detail.png" width=700 caption="Individual trace with span details" >}}

Once clicked a nested summary of details is shown right underneath the span. If you click on the little twistie left to `Tags` and `Processes` more span details are shown.

{{< figure src="images/jaeger_span_flask_span_details.png" width=700 caption="Individual trace with more Python span details" >}}

Here you can also get detailed information about the OpenTelemetry collection components being used, e.g. library name, SDK version etc.

Repeat the same steps and also check the details of a span within the Java component.
Pick the one which says `todobackend-springboot TodoRepository.save`.
This will list the details of the span which are provided by the implementation of the OpenTelemetry agent. As you can see here it's provided by the Java SDK and the Spring Data library in particular.

{{< figure src="images/jaeger_span_spring_details.png" width=700 caption="Individual trace with more Spring span details" >}}

This also shows that the amount of information can totally differ between different agent implementation. They need to comply with a certain standard so that the information can be used and correlated, but the content may vary.

The instrumentation part of this lab will show how the information of a span can be customized.

Feel free to browse around and look into other span details of the trace.

### Simulation of a slow component

Due to the load generator and simple structure of the application the results in Jaeger won't have much deviation, so it's unlikely to spot an anomaly in behaviour here.

There is a simulated decrease in performance built-in, if you add an item called "slow".

Open the Python or Java frontend and submit an item with this name.

{{< figure src="images/todoui-frontend-slow.png" width=700 caption="Web UI with new item" >}}

You might notice a small delay after submitting the item. The thread is paused for a second.
It isn't much but it should however show easily how this can be spotted in the tool.

Repeat the search for all traces again like we've done before and you will see a spike in the response time. If it doesn't show up straight, give it a few seconds and repeat again.

{{< figure src="images/jaeger_traces_recent_slow.png" width=700 caption="slow" >}}

You can actually click directly on the dot in the overview and it will also take you to the corresponding trace. Alternatively you can select it from the list below of course.

{{< figure src="images/jaeger_trace_slow.png" width=700 caption="Web UI with new item" >}}

If you look at the trace now, it looks significantly different to what we've seen before. There is a dominating span compared to which all other spans look negclectably short in duration. The overall execution time is only slightly above a second whereas one span takes an entire second.

In a real world scenario isolating a poor performing component is probably not as obvious, but for showcasing how things work this should do for now.

Click on the long-running span to reveal more details.

{{< figure src="images/jaeger_trace_slow_details.png" width=700 caption="Web UI with new item" >}}

This shows the details provided by the OpenTelemetry agent. With the knowledge of package, class and method name it is easier to continue debugging at this point.

### Comparing traces

There are many things you can do with all the observability data being collected by OpenTelemetry.
This totally depends on the third-party tool functionality how the information is being displayed.

So the following part is less about what OpenTelemetry provides, but more like Jaeger evaluates it.

Search for all traces with the default settings again.
This time let's try to compare the Python to the Java invocation for the call to quuery all Todo items.

Once you have the list, select the `todoui-flask: /` and the `todoui-thymeleaf: GET /`.
There will probably be many invocations of this type by now, any pair of them will do.

{{< figure src="images/jaeger_traces_compare.png" width=700 caption="Web UI with new item" >}}

Click on "Compare Traces". A new window will show up displaying the traces in a visual flow next to each other. This also shows a different collection of spans for the Java and Python part to the left and an identical one for the backend on the right.

{{< figure src="images/jaeger_flow_compare.png" width=700 caption="Web UI with new item" >}}

Of course this also makes a lot of sense to compare multiple traces of exactly the same invocation type at different times. Hope you like this!