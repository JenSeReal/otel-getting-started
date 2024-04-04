---
title: "The current state of observability"
linktitle: "state of observability"
date: 2023-12-06T09:43:24+01:00
draft: false
weight: 1
---

### How we (traditionally) observe our systems

In every distributed system, there are two things we can observe: *transactions* and *resources*.
A transaction represents a set of orchestrated operations to fulfill a (larger) cohesive task.
For example, when a user sends a request to a distributed system, it is typically split up into several subrequests handled by different services.
Resources refer to the physical and logical components that make up the distributed system.

> Observability is a measure of how well the internal states of a system can be inferred from knowledge of its external outputs.

To make a system observable, we must model its state in a way that lets us reason about its behavior.
The traditional approach is to observe transactions and resources through a combination of *logs*, *metrics* and (sometimes) *traces*.

{{< figure src="images/metric_types.drawio.png" width=400 caption="The four common types of metrics: counters, gauges, histograms and summaries" >}}

A log is an append-only data structure that records events occurring in a system.
A log entry consists of a *timestamp* to denote when something happened and a *message* describing the details of a particular event.
Today, there are countless logging frameworks in existence, resulting in equally many log formats.
To a certain degree, this is understandable because different types of software often communicate different types of information.
Log messages of an HTTP web server are bound to look different from those of the kernel.
In general, we prefer structured logging.
Representing events as key/value pairs help make logs machine-readable since we can use common data interchange formats to encode and parse the data.
However, coming up with a log format is part of the problem.
The increasing degree of distribution in applications and the ephemeral nature of container-based environments meant that it was no longer feasible to log onto individual machines and sift through logs.
To address this, people developed logging systems and protocols to send logs to a central location.
This provided persistent storage, making it possible to search and filter logs, and more.

{{< figure src="images/logs.png" width=800 caption="Exemplary log files" >}}
While logging provides detailed information about individual events, we often want a more high-level representation of the state of the system.
This is where metrics come in.
A metric is a single numerical value that was derived by applying a statistical measure to a group of events.
In other words, metrics represent an aggregate.
Metrics are useful because their compact representation allows us to graph how our system changes over time.
Similar to logs, the industry developed systems to define the format of metrics, protocols to send data, time-series databases to store them, and frontends to make this data accessible to end-users.

{{< figure src="images/distributed_system.drawio.png" width=800 caption="Exemplary architecture of a distributed system" >}}
As distributed systems grew in complexity, it became clear that logging systems struggled with debugging problems efficiently at scale.
During an investigation, one typically has to reconstruct the chain of events that led to a particular problem.
On a single machine, stack traces are a great way to track an exception to a line of code.
In a distributed environment, we don't have this luxury.
Instead, we spend lots of manual labor filtering events before we find something of interest, followed by cumbersome analysis trying to identify and understand the larger context.
Recognizing this problem, Google developed [Dapper](https://storage.googleapis.com/pub-tools-public-publication-data/pdf/36356.pdf), which popularized the concept of distributed tracing.
Essentially, tracing is logging on steroids.
Adding transactional context to logs and indexing based on this information, we can reconstruct the journey of requests within the system.

{{< figure src="images/three_pillars_observability.jpg" width=400 caption="The three pillars of observability, including metrics, traces and logs" >}}

Together, logs, metrics, and traces are often referred to as *the three pillars of observability*.
These pillars provide a great mental framework for categorizing different types of telemetry.
It emphasizes that every telemetry signal has its unique strength and that combining their insights is essential to yield a foundation for an observable system.
However, the monumental connotation of the term "pillars" is deceptive.
It suggests that current practices in observability are the result of deliberate design by great architects and are set in stone.
In reality, it emerged organically through a series of responses to address the limitations of systems that existed at the time.

### Why the current approach to telemetry systems is flawed

{{< figure src="images/xkcd_927_standards.png" width=400 caption="[XKCD](https://xkcd.com/927/)" >}}

With loads of open-source and commercial observability solutions available on the market, you might (rightly) be asking yourself why OpenTelemetry exists or why there is currently so much hype around it.

In the past, telemetry systems were built as standalone end-to-end solutions for a specific purpose.
The reason is simple.
The best way to build a capable system is when the scope of the problem is as narrow as possible and everything is under your control.
For example, a metrics solution typically provides its own instrumentation mechanisms, data models, protocols, and interchange formats to transmit telemetry to a backend, and tools to analyze the collected data.
This style of thinking is called [vertical integration](https://en.wikipedia.org/wiki/Vertical_integration).
To answer the question of OpenTelemetry's popularity, let's look at two major problems with this approach.

{{< figure src="images/correlate_across_datasets.png" width=700 caption="Correlated telemetry data" >}}

First, there are deficits in the *quality* of telemetry data.
To illustrate this, let's look at a typical process of a root cause investigation.
Often, the first indicator of a potential problem is an anomaly in a metric dashboard.
After the operator confirms the incident is worth investigating, we have to form an initial hypothesis.
The only information we currently have is that something happened at a particular point in time.
Therefore, the first step is to use the metrics system to look for other metrics showing temporally correlated, abnormal behavior.
After making an educated guess about the problem, we want to drill down and investigate the root cause of the problem.
To gain additional information, we typically switch to the logging system.
Here, we write queries and perform extensive filtering to find log events related to suspicious metrics.
After discovering log events of interest, we often want to know about the larger context the operation took place in.
Unfortunately, traditional logging systems lack the mechanisms to reconstruct the chain of events in that particular transaction.
Traditional logging systems often fail to capture the full context of an operation, making it difficult to correlate events across different services or components. They frequently lack the ability to preserve critical metadata, such as trace IDs or span IDs, which are essential for linking related events together. This limitation results in fragmented views of the system's behavior, where the story of a single operation is spread across multiple logs without a clear narrative. Furthermore, the absence of standardized query languages or interfaces adds to the difficulty of searching and analyzing logs effectively, as operators must rely on custom scripts or manual filtering to uncover patterns and anomalies.

Switching the perspective from someone building an observability solution to someone using it reveals an inherent disconnect.
The real world isn't made up of logging, metrics, or tracing problems.
Instead, we have to move back and forth between different types of telemetry to build up a mental model and reason about the behavior of a system.
Since observability tools are silos of disconnected data, figuring out how pieces of information relate to one another causes a significant cognitive load for the operator.

Another factor that makes root cause analysis hard is that telemetry data often suffers from a lack of consistency. This leads to difficulties in correlating events across different services or components, as there is no standardized way to identify related events, such as through trace IDs or span IDs. Additionally, there is no straightforward method to integrate multiple solution-specific logging libraries into a coherent system, resulting in fragmented and disjointed views of the system's behavior.

<!-- lack of an instrumentation standard -->
The second major deficit is that vertical integration means that instrumentation, protocols, and interchange formats are tied to a specific solution.
This creates a maintenance nightmare for everyone involved.
<!-- end user  -->
Let's put on the hat of an end user.
After committing to a solution, the application contains many solution-specific library calls throughout its codebase.
To switch to another observability tool down the line, we would have to rip out and replace all existing instrumentation and migrate our analysis tooling.
This up-front cost of re-instrumentation makes migration difficult, which is a form of vendor lock-in.
<!-- library developers -->
Let's look at this from the perspective of open-source software developers.
Today, most applications are built on top of open-source libraries, frameworks, and standalone components.
With a majority of work being performed outside the business logic of the application developer, it is crucial to collect telemetry from open-source components.
The people with the most knowledge of what is important when operating a piece of software are the developers and maintainers themselves.
However, there is currently no good way to communicate through native instrumentation.
One option would be to pick the instrumentation of an observability solution.
However, this would add additional dependencies to the project and force users to integrate it into their system.
While running multiple logging and metrics systems is impractical but technically possible, tracing is outright impossible as it requires everyone to agree on a standard for trace context propagation to work.
A common strategy for solving problems in computer science is by adding a layer of indirection.
Instead of embedding vendor-specific instrumentation, open-source developers often provide observability hooks.
This allows users to write adapters that connect the open-source component to their observability system.
While this approach provides greater flexibility, it also has its fair share of problems.
For example, whenever there is a new version of software, users have to notice and update their adapters.
Moreover, the indirection also increases the overhead, as we have to convert between different telemetry formats.
<!-- observability vendor -->
The last part of the equation is the observability vendors themselves.
At first glance, vendors appear to be the only ones profiting from the current situation.
In the past, high-quality instrumentation was a great way to differentiate yourself from the competition.
Moreover, since developing integrations for loads of pre-existing software is expensive, the observability market had a relatively high barrier to entry.
With customers shying away from expensive re-instrumentation, established vendors faced less competition and pressure to innovate.
However, they are also experiencing major pain points.
The rate at which software is being developed has increased exponentially over the last decade.
Today's heterogeneous software landscape made it infeasible to maintain instrumentation for every library, framework, and component.
As soon as you start struggling with supplying instrumentation, customers will start refusing to adopt your product.
As a result, solutions compete on who can build the best n-to-n format converter instead of investing these resources into creating great analysis tools.
Another downside is converting data that was generated by foreign sources often leads to a degradation in the quality of telemetry.
Once data is no longer well-defined, it becomes harder to analyze.
