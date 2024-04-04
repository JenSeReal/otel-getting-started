+++
title = "manual instrumentation"
menuTitle = "manual"
draft = false
weight = 1
+++

<!-- Welcome to the first lab!
This lab looks at how to manually instrument an application by directly using OpenTelemetry's API and SDK.
In doing so, we explore how each signal works.
Thereby, we hope you gain an understanding of the fundamental concepts and terminology used by OpenTelemetry. -->


{{< figure src="images/otel_architecture_impl.drawio.svg" width=700 caption="placeholder" >}}

The specification is realized through a collection of **language-*specific* implementations**.
OpenTelemetry supports a wide-range of popular [programming languages](https://opentelemetry.io/docs/instrumentation/#status-and-releases).
The implementation of a telemetry signal is mainly divided into two separate parts: the *API* and the *SDK*.
The API provides the set of interfaces to embed vendor-agnostic instrumentation into our applications and libraries.
These interfaces adhere to what was defined in OpenTelemetry's specification.
Then, there are *providers*, which implement the API.
A provider contains the logic to generate, process/aggregate and transmit the telemetry for the programming language of choice.
On startup, the application registers a provider for every type of signal.
Thereby, all API calls will be forwarded to the designated provider.
OpenTelemetry provides an SDK for every language it supports
This SDK contains a set of official providers that serve the reference implementation of the API.
There are several reasons for why OpenTelemetry separates the API and SDK like this.
First, let's consider the case of an open-source developer who wants to embed instrumentation in their code.
The implementation of a telemetry signal likely relies on a number of other dependencies.
Forcing these dependencies onto your users is problematic, as it may cause dependency conflicts in their environments.
In contrast, APIs merely consists of a set of interfaces and constants.
By separating both open-source developers can depend on the lightweight API, while users are free to choose an implementation that doesn't cause conflicts with their specific software stack.
Another benefit of this design is that it allows us to embed observability into software, without users having to pay the runtime cost if they don't need it.
Whenever we don't register a provider for a signal, OpenTelemetry will default to a special provider that translates API calls into no-ops.

However, it comes with its own set of trade-offs. Implementing OpenTelemetry can introduce complexity to an application, potentially impacting performance, when configured wrong, and may lead to vendor lock-in if heavily invested in a specific implementation. As a relatively new project, it may face challenges with adoption and compatibility, and while it aims to be vendor-agnostic, there is still a risk of vendor lock-in. Customization and flexibility may be limited compared to tailored solutions for specific use cases, and there can be a learning curve associated with understanding OpenTelemetry's concepts and APIs. Maintenance and support, particularly for organizations that rely on open-source projects, may require additional investment. Integration with existing systems can be challenging and may require extra effort. Costs may also be incurred depending on the scale of implementation and the need for additional services or support. Lastly, while OpenTelemetry has a growing community, it may not yet have the same level of community support or ecosystem of tools and integrations as more established projects. Additionally, it is important to consider that alternative implementations might offer better performance, as the SDK is designed to be extensible and general-purpose. This implies that while the SDK provides a robust framework for observability, it may not be the most optimized solution for every scenario. It is essential to weigh these trade-offs against the benefits of OpenTelemetry to determine if it is the right fit for a particular application or organization. But if OpenTelemetry is used in the right way and configured well - the benefits might