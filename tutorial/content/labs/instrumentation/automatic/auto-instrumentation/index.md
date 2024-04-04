---
title: "auto-instrumentation"
draft: false
weight: 3
---

Instrumentation libraries simplify the experience of adopting OpenTelemetry by injecting instrumentation into popular third-party libraries and frameworks.
This is especially useful in situations where we don't want to write manual instrumentation, but no native instrumentation is available.
Since instrumentation libraries are developed and maintained by members of the OpenTelemetry community, we
- don't have to wait for native instrumentation
- don't put burden on the back of the library or framework maintainer

A common way to take advantage of instrumentation libraries is in combination with OpenTelemetry's auto-instrumentation.
In contrast to the API and SDK, auto-instrumentation allows us to dynamically inject observability into the application without having to make changes to the source code.

Generally speaking, auto-instrumentation is implemented by some kind of agent or runner.
In this lab, we'll use a Java application to understand what this could look like.

### byte code manipulation via Java agent
```java
public class MyAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
        inst.addTransformer(new MyTransformer());
    }
}

public class MyTransformer implements ClassFileTransformer {
    @Override
    public byte[] transform(
            ClassLoader loader,
            String className,
            Class<?> classBeingRedefined,
            ProtectionDomain protectionDomain,
            byte[] classfileBuffer
    ) {
        // Perform bytecode transformation
        // ...

        // Return the modified bytecode
        return modifiedBytecode;
```

You'll likely know that `main` method is the entry point of Java program.
In addition to that, the Java Virtual Machine (JVM) also supports two other types of entry points: `premain` and `agentmain`.
Both `premain` and `agentmain` have an optional parameter to pass an `Instrumentation` instance as an argument to the method.
Java's built-in Instrumentation interface provides access to low-level functionality of the JVM.
It operates on a byte code level and provides mechanisms to modify and inspect the behavior of Java applications at runtime.
Most notables, the `ClassFileTransformer` API allows you to take a class file (basically a compilation unit of a .java file) and manipulates the byte array before it is loaded.
Instead of trying to identify classes and methods and edit the byte code directly, we typically use libraries such as [Byte Buddy](https://bytebuddy.net/) that make these byte code transformations more convenient.
With the help of these tools, we are able to develop static and dynamic Java agents.
On a high level, auto-instrumentation agents of different APM vendors (e.g. Instana, ...) work similarly.
On startup, the agent discover what clients (e.g. JDBC driver, HTTP Client) are used by the application and decides whether to instrument them.
After identifying the methods of interest (e.g. that do the HTTP calls), a transformer rewrites the byte array to inject the custom instrumentation logic that captures telemetry.
The transformer returns the modified byte code.
To attach the agent to the target application, its program is packaged as a separate .jar file and passed to the Java runtime via the `-javaagent` argument.
This allows the agent to modify the byte code of classes as they are loaded into the Java Virtual Machine (JVM).

Fortunately, OpenTelemetry simplifies this process by providing an [`opentelemetry-javaagent.jar`](https://github.com/open-telemetry/opentelemetry-java-instrumentation).
This jar includes instrumentation libraries for various frameworks and third-party libraries. It also contains components like OpenTelemetryAgent and AgentInstaller, which initiate the process, analyze the application, detect, and load available third-party instrumentation libraries.
These components leverage the mentioned mechanisms to adapt the byte code of Java classes at runtime.
Additionally, the OpenTelemetryInstaller configures emitters based on configuration options provided at invocation time (e.g., via the -D flag or Java properties file) to produce and deliver telemetry without any additional work on part of the user.

This section should highlight that auto-instrumentation is built on mechanisms specific to the given programming language.
Other languages may lack similar native capabilities.
Therefore, not all languages come with support for auto-instrumentation.

#### excercise

```sh
git clone https://github.com/jtl-novatec/otel-training-tracing-lab.git
cd ./otel-training-tracing-lab/
```
Clone the repository and change into the directory for this lab.
`/src` contains a Java service that was build using Spring Boot.
Image this is a legacy application and that observability wasn't considered during the development process.
Hence, the service currently lacks native instrumentation.
How would we start insights into the application?
With manual instrumentation, we first would have to get familiar with the codebase to know what to instrument.
Then, we would need to write the instrumentation, which (as you have seen) can take quite a bit of work effort.

Therefore, the fastest way to generate telemetry is to leverage OpenTelemetry's instrumentation libraries and auto-instrumentation.

```Dockerfile { title="app.Dockerfile" }
# build app
FROM maven:3-eclipse-temurin-21 AS build
# ...

# application don't need full JDK at runtime
FROM eclipse-temurin:17-jre-alpine
# ...

# run app
ENTRYPOINT ["java","-cp","app:app/lib/*", "org.springframework.samples.petclinic.PetClinicApplication"]
```

To make your life a bit easier, `./deployment/docker/app.Dockerfile` already contains the dockerized Java application for you.
Open it and have a brief look at it.
It is a multi-stage Dockerfile that basically does three things.
First, it uses maven to compile the source code into a `.jar` byte code.
Then, it copies the files from build stage into another container, since the application doesn't require the full JDK and build tools at runtime.
Finally, the `ENTRYPOINT` runs the application on startup.

<!--
It contains two stages, one for building the Java application through maven and one to run it.
Let's create the container image via `docker build -t myorg/myapp .`
You can start the container by executing `docker run -it -p 8080:8080 myorg/myapp`.
Looking at `pom.xml` and theh boot process reveals that the application is built using Spring Boot.
The application also uses other libraries besides the Spring framework (e.g. JDBC, a hsqldb ).
As mentioned earlier, OpenTelemetry's Java agent  a rich set of [instrumentation libraries](https://github.com/open-telemetry/opentelemetry-java-instrumentation/tree/main/instrumentation).
-->

```Dockerfile { title="app.Dockerfile" }
# get java agent for auto instrumentation
ARG OTEL_AGENT_VERSION=1.31.0
ADD https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases/download/v$OTEL_AGENT_VERSION/opentelemetry-javaagent.jar ./otel/opentelemetry-javaagent.jar
```
To add auto-instrumentation, we must first get a copy of OpenTelemetry's Java Agent.
Fortunately, the [releases](https://github.com/open-telemetry/opentelemetry-java-instrumentation/releases) of the [repository](https://github.com/open-telemetry/opentelemetry-java-instrumentation) already provides a pre-compiled .jar archive for us.
Let's use Docker's `ADD` command to copy the jar from the URL to the container's file system.

```Dockerfile { title="app.Dockerfile" }
ENTRYPOINT ["java","-cp","app:app/lib/*", "-javaagent:otel/opentelemetry-javaagent.jar", "org.springframework.samples.petclinic.PetClinicApplication"]
```
To manipulate the byte code of the application, we'll simply pass the Java Agent to the runtime using the `--javaagent` argument.


```sh { title="terminal" }
docker build -f deployment/docker/app.Dockerfile -t myorg/myapp .
docker run -it -p 8080:8080 myorg/myapp
```

After injecting the agent, let's build the application with and start the container.

```sh
[otel.javaagent 2024-01-17 09:24:06:037 +0000] [main] INFO io.opentelemetry.javaagent.tooling.VersionLogger - opentelemetry-javaagent - version: 1.31.0

  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v3.2.1)
```

```sh
[otel.javaagent 2024-01-17 09:25:06:631 +0000] [OkHttp http://localhost:4317/...] WARN io.opentelemetry.exporter.internal.grpc.GrpcExporter - Failed to export metrics. Server responded with gRPC status code 2. Error message: Failed to connect to localhost/127.0.0.1:4317
```

If everything works as expected, a `otel.javaagent` log message should appear before the Spring Boot application starts.
After boot process completes, log messages appear which indicate that the agent failed to export metrics.
We previously used the SDK to define instrumentation *and* a pipeline of how telemetry should be processed and where it should go.
By default, the agent tries to forward telemetry to a local collector listening on `localhost:4317`.
At moment, we neither have a Collector nor telemetry backends running.
Inside `/deployments/docker`, we prepared a `compose.yaml` file that simulates a complete observability stack.
- Prometheus for metrics
- Jaeger for traces

To ingest telemetry into these backends, we must supply configuration to the OpenTelemetry agent.
It receives user-defined configuration options and automatically sets up the SDK (i.e. the tracer, meter and logger provider) for us.
The agent is designed to be highly-configurable and provides a bunch of parameters to control various ...
Here, we'll focus on the essentials, which include:
- what exporter to use
- where the backends are
- resource attached to telemetry

The agent can be configured with the help of environment variables, configuration files and by passing command line arguments.

```
- configure the agent
- docker-compose.yaml with backend
```

```sh
docker compose up --detach
```

With everything setup, let's finally start the demo environment.
- Open browser and go to
  - Jaeger
    - generate traffic
    - see trace with breakdown of what is being invoked inside the application
      - methods
      - database calls
      - tomcat web server
  - Grafana
    - view metric dashboards

### limitations of auto-instrumentation

A major advantage of dynamically attaching instrumentation at runtime is that we don't have to make modifications to the application's source code.
Auto-instrumentation provides a great starting point when trying to instrument an existing application.
The observability insights it provides are sufficient for many, while avoiding the significant time investment and understanding of OpenTelemetry's internals that is required with manual instrumentation.
However, as you might have guessed, it is not a magic bullet as there are inherent limitations to what auto-instrumentation can do for us.
Building on top of instrumentation libraries, auto-instrumentation inherently capture telemetry data at *known* points in a library or framework.
These points are deemed interesting from an observability perspective because they relate to actions such an incoming HTTP request, making a database query, etc.

```
show source code custom method without annotation
```
However, sometimes we want to observe aspects of our application that don't naturally align with these standard instrumentation points.
Developers often encapsulate related logic in dedicated functions to improve code maintainability and organization.
The OpenTelemetry agent may lack awareness of these custom functions.
It has no way of knowing whether they are important and what telemetry data to capture from them.

```
```
Let's test this.
Exec into our utility container `docker exec ...` and use `curl ....` to issue a request to the endpoint which calls our custom method.
Go to Jaeger and find the corresponding trace.
As you'll see, the trace currently doesn't contain a span associated with our custom method.
Such gaps in observability may mean that you may miss critical insights in the behavior of the application.
However, since they aren't mutually exclusive, we can always enhance auto- with manual instrumentation.

```
pom.xml
```
```
import package
```
To achieve this, we must install the API and SDK dependencies for manual instrumentation by adding them to `pom.xml`.
Next, open up `xyz.java` and specify the respective imports as shown above.
Now, we can add the `@WithSpan` annotation to our custom method.
Rebuild the application.
Again, use the `curl` command to issue a request and look at the corresponding trace in Jaeger.
You should now see that a dedicated Span was created for the custom method.

```
add  @SpanAttribute
```
We might want to include some additional context in the Span.
For example, the span should include the value of a parameter passed to the function.

## finish

Congratulations on successfully completing this chapter!
This lab illustrated how auto-instrumenation can perform work, which previously required us to write manual instrumentation.
It showed how OpenTelemetry allows us to extend automatic with custom instrumentation to gain additional visibility where it is needed.
It is important to emphasize that instrumentation libraries and agents are not a drop-in replacement for manual instrumentation.
Library instrumentation and agent-based approaches offer convenience and quick setup, manual instrumentation using OpenTelemetry's API and SDK provides more control and flexibility.
For example, auto-instrumentation might instrument aspects of the code that are not relevant to the specific monitoring goals.
While OpenTelemetry ships with powerful procession tools to shape telemetry, manual instrumentation allows us to precisely instrument only what is necessary.
In addition, there's a fundamental tension between the desire for zero-effort, minimally invasive observability and the shift-left approach that advocates for making observability an integral part of the development process.
Last (and certainly not least), library and framework instrumentation only cover generic aspects of an application.
To make a system truly observable, one often must record telemetry specific to the domain of the application.
This goes beyond what automatic instrumentation can provide, because it requires a higher-level understanding of the code and business.
It is important to emphasize that both approaches are not mutually exclusive.
Therefore, it is crucial to find the right balance between them to create an observable system without imposing undue burdens on the development team.


<!-- NOTES  -->

<!--
- Agent Extensions
  - demo von Matthias verwendet annotations das eine custom Methode als span im trace angezeigt wird
  - es gibt scheinbar auch die möglichkeit Extensions für custom instrumentaion zu schreiben
    - InstrumentationModule and TypeInstrumentation
  - related links:
    - https://github.com/open-telemetry/opentelemetry-java-instrumentation/blob/main/docs/contributing/writing-instrumentation-module.md
    - https://www.elastic.co/blog/auto-instrumentation-of-java-applications-opentelemetry
    - https://www.youtube.com/watch?v=hXTlV_RnELc
    - https://opentelemetry.io/docs/instrumentation/java/automatic/extensions/
    - https://github.com/open-telemetry/opentelemetry-java-instrumentation/tree/main/examples/extension
-->