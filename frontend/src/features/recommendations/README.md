# Recommendations Feature

Personalized "For You" recommendations based on user interests and behavior.

## Overview

The recommendations feature provides intelligent content suggestions using:
- **Personalized Recommendations**: Based on user profile and history
- **Responsive Grid**: Adapts to screen size (1/2/3 columns)
- **Smart Caching**: 10-minute stale time for performance
- **Graceful Degradation**: Handles errors without breaking UI

## Architecture

```
recommendations/
├── api.ts                              # Recommendations API client
├── types.ts              