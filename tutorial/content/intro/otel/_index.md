+++
title = "promise of OpenTelemetry"
draft = false
weight = 2
+++

### history

OpenTelemetry is the result of the merger from OpenTracing and OpenCensus. Both of these products had the same goal - to standardize the instrumentation of code and how telemetry data is sent to observability backends. Neither of the products could solve the problem independently, so the CNCF merged the two projects into OpenTelemetry. This came with two major advantages. One both projects joined forces to create a better overall product and second it was only one product and not several products. With that standardization can be reached in a wider context of telemetry collection which in turn should increase the adoption rate of telemetry collection in applications since the entry barrier is much lower. The CNCF describes OpenTelemetry as the next major version of OpenTracing and OpenCensus and as such there are even migration guides for both projects to OpenTelemetry.

### promises

At the time of writing, OpenTelmetry is under active development and is one of the fastest-growing projects in the CNCF.
OpenTelemetry is receiving so much attention because it promises to be a fundamental change in the way we produce telemetry and address many of the problems mentioned earlier.
Previously, the rate of innovation and conflicts of interest prevented us from defining widely adopted standards for telemetry.
At the time of writing, the timing and momentum of OpenTelemetry appear to have a realistic chance of pushing for standardization of common aspects of telemetry across vendors.
A key promise of OpenTelemetry is that you "instrument code once and never again" and can "use your instrumentation everywhere".
There are multiple factors behind this.
First, OpenTelemetry recognizes that, should its efforts be successful, it will be a core dependency for countless software projects.
Therefore, its telemetry signal specifications follow strict processes to provide [long-term stability guarantees](https://opentelemetry.io/docs/specs/otel/versioning-and-stability/).
Once a signal is declared stable, clients will never experience a breaking API change.
The second aspect is that OpenTelemetry separates the system that produces telemetry from the one that analyzes the data.
Open and vendor-agnostic instrumentation to generate, collect, and transmit telemetry marks a fundamental shift in how observability vendors compete for your business.
Instead of having to put significant investment in building instrumentation, observability vendors must differentiate themselves by building feature-rich analysis platforms with great usability.
Moreover, users no longer have to commit to the observability solution they choose during development.
Once you migrate over to OpenTelemetry, you can easily move between different vendors without having to re-instrument your entire system.
Similarly, developers of open-source software can add native instrumentation to their projects without introducing vendor-specific code and creating burdens for downstream users.
By avoiding all these struggles, OpenTelemetry pushes for observability to become a first-class citizen during development.
The goal is to make software observable by default.
Last (and definitely not least), OpenTelemetry pushes for a change in how we think about and use telemetry.
Instead of having three separate silos for logs, metrics, and traces, OpenTelemetry follows a paradigm of linking telemetry signals together.
With context creating touch points between signals, the overall value and usability of telemetry increase drastically.
For instance, imagine the ability to jump from a conspicuous statistics in a dashboard straight to the related logs.
Correlated telemetry data helps to reduce the cognitive load on humans operating complex systems.
Being able to take advantage of linked data will mark a new generation of observability tools.
While only time will tell if it can live up to its promises, let's dive into its architecture to learn how it tries to achieve these goals.

In order to fulfill its objectives, OpenTelemetry is engineered to provide a uniform set of APIs and libraries that facilitate the instrumentation, generation, collection, and export of telemetry data. As a vendor-agnostic, independent, and heterogeneous layer, it serves as a foundational element for expressing telemetry data, capable of interfacing with a broad spectrum of downstream analysis, querying, alerting, and visualization tools. This design allows for the implementation of OpenTelemetry's capabilities within various libraries, frameworks, and programming languages, streamlining the adoption process. Furthermore, OpenTelemetry's principles ensure that it remains compatible with a myriad of monitoring and observability tools, guaranteeing long-term stability and consistency in telemetry data formats.