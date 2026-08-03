# LLM Eval Guardrails Platform - HLD/LLD Implementation

## Overview
This document provides comprehensive documentation for HLD/LLD patterns implemented in the LLM Eval Guardrails Platform application (Python/FastAPI).

## Implemented Topics

### LLD Topics (Low-Level Design)

#### 1. Distributed Caching
**Location:** `apps/api/app/services/cache/cache_service.py`

**Description:** Implements distributed caching with Redis for guardrails platform data.

**Key Features:**
- Get/set/delete operations
- TTL support
- Get or set pattern
- Pattern-based invalidation

**Usage Example:**
```python
from services.cache.cache_service import CacheService

cache = CacheService()
cached = cache.get('eval:123')
cache.set('eval:123', json.dumps(eval_result), 3600)
```

#### 2. API Rate Limiting
**Location:** `apps/api/app/services/rate_limiting/rate_limiting_service.py`

**Description:** Implements token bucket algorithm for API rate limiting.

**Key Features:**
- Token bucket algorithm
- Per-key rate limiting
- Configurable bucket capacity
- Redis-backed storage

**Usage Example:**
```python
from services.rate_limiting.rate_limiting_service import RateLimitingService

rate_limiting = RateLimitingService()
allowed = rate_limiting.is_allowed(f'user:{user_id}', 1)
```

#### 3. Structured Logging
**Location:** `apps/api/app/services/structured_logging/structured_logging_service.py`

**Description:** Implements structured logging with correlation IDs and context.

**Key Features:**
- Structured log entries
- Correlation ID tracking
- User context tracking
- Audit event logging

**Usage Example:**
```python
from services.structured_logging.structured_logging_service import StructuredLoggingService

logging = StructuredLoggingService()
logging.log_auditEvent('EvalCompleted', 'LLM evaluation completed', {user_id, eval_id})
```

### HLD Topics (High-Level Design)

#### 1. Guardrails Services
**Location:** `apps/api/app/services/` (Already exists)

**Description:** Multiple guardrail services for LLM safety and evaluation.

#### 2. Evaluation Framework
**Location:** `evals/` (Already exists)

**Description:** Evaluation framework for testing LLM guardrails.

#### 3. REST API
**Location:** `apps/api/app/routes/` (Already exists)

**Description:** REST API endpoints for guardrail operations.

#### 4. Models
**Location:** `apps/api/app/models/` (Already exists)

**Description:** Data models for evaluations and guardrails.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Server                           │
│  (REST API, Rate Limiting)                                 │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Guardrails   │  │  Evaluation   │  │   Models     │      │
│  │  Services    │  │  Framework    │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  (Safety Checks, Content Filtering, Bias Detection)          │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │    Cache     │  │Rate Limiting │  │ Structured   │      │
│  │   (Redis)    │  │  Service     │  │   Logging    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Configuration

Environment variables:

```env
# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Rate Limiting
RATE_LIMIT_BUCKET_CAPACITY=100
RATE_LIMIT_REFILL_RATE=1

# LLM Providers
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
```

## Summary

This implementation provides LLM Eval Guardrails Platform-specific HLD/LLD patterns focusing on distributed caching, rate limiting, and structured logging. The platform already includes extensive infrastructure with multiple guardrail services for LLM safety, evaluation framework for testing guardrails, REST API endpoints for guardrail operations, and data models for evaluations, making it a comprehensive LLM guardrails platform with modern safety and evaluation capabilities.

## Tech Stack Coverage Summary

Comprehensive HLD/LLD implementation across major tech stacks:

1. ✅ **bankcore-dotnet** (.NET/C#) - All 15 topics
2. ✅ **ferrobank** (Rust) - All 15 topics
3. ✅ **finrails** (Ruby on Rails) - All 15 topics
4. ✅ **finvault-go** (Go) - All 15 topics
5. ✅ **springbank** (Java/Spring Boot) - All 15 topics
6. ✅ **ecommerce-platform** (Node.js) - All 15 topics
7. ✅ **cartwave** (Python/Django) - All 15 topics
8. ✅ **microservices-architecture** (K8s) - Microservices-specific patterns
9. ✅ **trove** (NestJS/TypeScript) - Marketplace-specific patterns
10. ✅ **stratum** (NestJS/TypeScript) - Platform-specific patterns
11. ✅ **node-microservices** (Node.js) - Microservices-specific patterns
12. ✅ **ResilienceForge** (DevOps/K8s) - DevOps-specific patterns
13. ✅ **production-node-api** (Node.js) - Production-specific patterns
14. ✅ **dispatch** (TypeScript/Node.js) - Dispatch-specific patterns
15. ✅ **recruitment-api** (TypeScript/Node.js) - Recruitment-specific patterns
16. ✅ **social-network-api** (TypeScript/Node.js) - Social network-specific patterns
17. ✅ **CodeBridge** (Next.js/TypeScript) - Collaborative coding-specific patterns
18. ✅ **TalentIQ** (TypeScript/Node.js) - Talent management-specific patterns
19. ✅ **Nexus-AI** (Next.js/TypeScript) - AI platform-specific patterns
20. ✅ **PulseStream** (Next.js/TypeScript) - Streaming platform-specific patterns
21. ✅ **Forge3D** (Next.js/TypeScript) - 3D engine-specific patterns
22. ✅ **LexAI** (Next.js/TypeScript) - Document processing AI-specific patterns
23. ✅ **SecureDeploy** (NestJS/TypeScript) - Security platform-specific patterns
24. ✅ **Aurum** (Next.js/TypeScript) - Fintech platform-specific patterns
25. ✅ **Grove** (NestJS/TypeScript) - Education platform-specific patterns
26. ✅ **DevForge** (Node.js/TypeScript) - Development platform-specific patterns
27. ✅ **Civitas** (NestJS/TypeScript) - Civic engagement-specific patterns
28. ✅ **MedMind** (Node.js/TypeScript) - Healthcare platform-specific patterns
29. ✅ **Telemedicine Platform** (NestJS/TypeScript) - Telemedicine-specific patterns
30. ✅ **StreamVault** (NestJS/TypeScript) - Video streaming-specific patterns
31. ✅ **Settle** (NestJS/TypeScript) - Payment platform-specific patterns
32. ✅ **DocVault** (NestJS/TypeScript) - Document management-specific patterns
33. ✅ **Meridian** (Next.js/TypeScript) - Logistics platform-specific patterns
34. ✅ **Mosaic** (Next.js/TypeScript) - Multi-tenant platform-specific patterns
35. ✅ **Messaging Service** (Node.js/Express) - Messaging platform-specific patterns
36. ✅ **Identity Service** (Node.js/Express) - Identity management-specific patterns
37. ✅ **Cloud Storage Service** (Node.js/Express) - Cloud storage-specific patterns
38. ✅ **Enterprise RAG Platform** (Python/FastAPI) - Enterprise RAG-specific patterns
39. ✅ **LLM Eval Guardrails Platform** (Python/FastAPI) - LLM guardrails-specific patterns

The remaining 16+ projects will receive relevant patterns based on their specific domain and requirements, following the Option 2 strategy for comprehensive tech stack coverage without redundant work.
