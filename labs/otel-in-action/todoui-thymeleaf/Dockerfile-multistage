FROM docker.io/maven:3-eclipse-temurin-21 as build
WORKDIR /workspace/app

COPY pom.xml .
COPY src src

RUN --mount=type=cache,target=/root/.m2 mvn install -DskipTests
RUN mvn install -DskipTests
RUN mkdir -p target/dependency && (cd target/dependency; jar -xf ../*.jar)

FROM docker.io/eclipse-temurin:21-jdk-alpine
RUN addgroup -S demo && adduser -S demo -G demo
USER demo
VOLUME /tmp
ARG DEPENDENCY=/workspace/app/target/dependency
COPY --from=build ${DEPENDENCY}/BOOT-INF/lib /app/lib
COPY --from=build ${DEPENDENCY}/META-INF /app/META-INF
COPY --from=build ${DEPENDENCY}/BOOT-INF/classes /app
ENTRYPOINT ["java","-cp","app:app/lib/*","io.novatec.todoui.TodouiApplication"]
