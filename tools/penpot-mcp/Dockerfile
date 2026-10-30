FROM node:22.23.3-bookworm-slim

ARG PENPOT_MCP_VERSION=2.17.0
ARG PNPM_VERSION=11.9.0

RUN npm install --global pnpm@${PNPM_VERSION}

WORKDIR /opt
RUN npm pack @penpot/mcp@${PENPOT_MCP_VERSION} \
 && tar xzf penpot-mcp-${PENPOT_MCP_VERSION}.tgz \
 && mv package penpot-mcp \
 && rm penpot-mcp-${PENPOT_MCP_VERSION}.tgz

WORKDIR /opt/penpot-mcp
RUN cp pnpm-lock.dist.yaml pnpm-lock.yaml \
 && pnpm -r install --frozen-lockfile \
 && pnpm run build

ENV PENPOT_MCP_SERVER_HOST=0.0.0.0 \
    PENPOT_MCP_PLUGIN_SERVER_HOST=0.0.0.0
