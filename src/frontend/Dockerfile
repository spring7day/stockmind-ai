# ============================================================
# Stage 1: Dependencies — install node_modules
# ============================================================
FROM node:20-alpine AS deps

WORKDIR /app

# Install libc compatibility layer for native modules
RUN apk add --no-cache libc6-compat

# Copy package files for layer caching
COPY package.json package-lock.json* ./

RUN npm ci --only=production

# ============================================================
# Stage 2: Builder — build the Next.js application
# ============================================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy all source files
COPY . .

# Set build-time environment variables
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build the application (produces .next/standalone)
RUN npm run build

# ============================================================
# Stage 3: Runner — minimal production image
# ============================================================
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy the standalone output from builder
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Set correct ownership
RUN chown -R nextjs:nodejs /app

USER nextjs

EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD wget -qO- http://localhost:3000/ || exit 1

# Start the Next.js standalone server
CMD ["node", "server.js"]
