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

<!-- 
However, it comes with its own set of trade-offs. 
Implementing OpenTelemetry can introduce complexity to an application, potentially impacting performance, when configured wrong, and may lead to vendor lock-in if heavily invested in a specific implementation. 
As a relatively new project, it may face challenges with adoption and compatibility, and while it aims to be vendor-agnostic, there is still a risk of vendor lock-in. 
Customization and flexibility may be limited compared to tailored solutions for specific use cases, and there can be a learning curve associated with understanding OpenTelemetry's concepts and APIs. 
Maintenance and support, particularly for organizations that rely on open-source projects, may require additional investment. 
Integration with existing systems can be challenging and may require extra effort. 
Costs may also be incurred depending on the scale of implementation and the need for additional services or support. 
Lastly, while OpenTelemetry has a growing community, it may not yet have the same level of community support or ecosystem of tools and integrations as more established projects. 
Additionally, it is important to consider that alternative implementations might offer better performance, as the SDK is designed to be extensible and general-purpose. 
This implies that while the SDK provides a robust framework for observability, it may not be the most optimized solution for every scenario. 
It is essential to weigh these trade-offs against the benefits of OpenTelemetry to determine if it is the right fit for a particular application or organization. 
But if OpenTelemetry is used in the right way and configured well - the benefits might
-->