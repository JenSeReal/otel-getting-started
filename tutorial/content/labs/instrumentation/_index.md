+++
title = "instrumentation"
draft = false
weight = 2
+++

The OpenTelemetry project is organized as a set of telemetry signals.
Every signal is developed as a stand-alone component (but OpenTelemetry also defines ways how to integrate them with one another).
Currently, OpenTelemetry incorporates (but isn't limited to) signals for tracing, metrics, logging and baggage.

{{< figure src="images/otel_architecture_spec.drawio.svg" width=700 caption="cross-language specification" >}}

At its core, every signal is defined by a **language-*agnostic* specification**, which ensures consistency and interoperability across various programming languages.
First, the specification includes definitions of terms to establish shared understanding and common vocabulary within the OpenTelemetry ecosystem.
Second, each telemetry signal provides an API specification.
The API specification defines the interface that all OpenTelemetry implementations must adhere to. This includes the methods that can be used to generate, process, and export telemetry data. By following the API specification, OpenTelemetry implementations can ensure that they are compatible with each other and can be used to collect and analyze telemetry data from a variety of sources.

The API specification is complemented by the SDK specification.
It serves as a guide for developers defining the requirements that an implementation of the API must meet to be compliant.
In here, OpenTelemetry specifies concepts around the configuration, processing, and exporting of telemetry data.
Last, the API specification contains a section to define aspect on the telemetry data.
This includes the concept of semantic conventions, which aim to standardize meaning and interpretation of telemetry data.
Ensuring that telemetry interpreted consistently regardless of the vendors involved fosters interoperability.
Finally, there specification also defines the OpenTelemetry Protocol (OTLP).

Using the SDK telemetry data can be generated within applications. This can be accomplished in two ways - automatic and manual. With automatic instrumentation there are predefined metrics, traces and logs that are collected within a library or framework. This will yield a standard set of telemetry data that can be used to getting started quickly with observability. Auto-instrumentation is either already added to a library or framework by the authors or can be added using agents, but we will learn about this later. With manual instrumentation more specific telemetry data can be generated. To use manual instrumentation the source code has to modified most of the time, except when you are using an agent like inspectIT Ocelot that can inject manual instrumentation code into your application. This allows for to collect more specific telemetry data that is tailored to your needs. Manual instrumentation is a big part of the following labs chapter.

The benefit of instrumenting code with OpenTelemetry to collect telemetry data is that the correlation of the previously mentioned signals is simplified since all signals carry metadata. Correlating telemetry data enables you to connect and analyze data from various sources, providing a comprehensive view of your system's behavior. By setting a unique correlation ID for each telemetry item and propagating it across network boundaries, you can track the flow of data and identify dependencies between different components. OpenTelemetry's trace ID can also be leveraged for correlation, ensuring that telemetry data from the same request or transaction is associated with the same trace. Correlation engines can further enhance this process by matching data based on correlation IDs, trace IDs, or other attributes like timestamps, allowing for efficient aggregation and analysis. Correlated telemetry data provides valuable insights for troubleshooting, performance monitoring, optimization, and gaining a holistic understanding of your system's behavior. In the labs' chapter you will see how correlated data looks like. Traditionally this had to be done by hand or just by timestamps which was a tedious task.

To ensure that the collected telemetry data can be collected across different frameworks, libraries or programming languages a vendor-neutral protocol was set into place. The OpenTelemetry Protocol (OTLP) is an open-source protocol for collecting and transmitting telemetry data, to back-end systems for analysis and storage. It defines a standardized data model, encoding format, and transport mechanisms to enable interoperability between telemetry tools and services from different vendors. By standardizing the way telemetry data is collected and transported, OTLP simplifies the integration of telemetry tools and services, improves data consistency, and facilitates data analysis and visualization across multiple technologies and environments.

OTLP offers three transport mechanisms for transmitting telemetry data: HTTP/1.1, HTTP/2, and gRPC. When using OTLP, the choice of transport mechanism depends on application requirements, considering factors such as performance, reliability, and security. OTLP data is often encoded using the Protocol Buffers (Protobuf) binary format, which is compact and efficient for network transmission and supports schema evolution, allowing for future changes to the data model without breaking compatibility. Data can also be encoded in the JSON file format which allows for a human-readable format with the disadvantage of higher network traffic and larger file sizes. The protocol is described in the OpenTelemetry Protocol Specification.