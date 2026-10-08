# DGM-MAT — Archived Unproven Provider Stack

Date: 2026-10-08

This archive preserves provider implementations and orchestration that were removed from canonical DGM-MAT after structural and historical audit.

## Why quarantined

The provider adapters contained multiple false-reality behaviors:

- chat() methods returned placeholder strings instead of performing real provider requests;
- several health checks marked a provider `ok` merely because an API key/configuration existed;
- ChatGPT authentication returned success without verifying an authenticated session;
- the provider mesh ranked and selected providers whose implementations were not real execution paths;
- the Open WebUI adapter was explicitly placeholder-only;
- the Ollama adapter was a real HTTP adapter but had no production callers or integration contract;
- browser recovery/provider code had no production callers in the canonical runtime.

The provider mesh and adapter tests encoded these assumptions, including assertions that placeholder responses and hard-coded capability scores were authoritative.

## Preserved material

- ChatGPT, Claude, Custom, DeepSeek, Gemini, Grok, OpenAI, OpenRouter, OpenWebUI, PoisonGPT, Proxima, Qwen and Z adapters;
- browser manager/recovery connectors;
- local AI fabric, including the real Ollama HTTP adapter and placeholder OpenWebUI adapter;
- provider mesh orchestration/ranking/consensus components;
- tests that depended on the unproven provider stack.

## What remains canonical

`core/providers/base/provider_base.py` and the provider registry contract remain because they can support future real provider adapters. No provider is considered healthy merely because an adapter class exists.

Actual Ollama connectivity remains a separate capability and is governed by observed local runtime evidence and the low-memory policy. It is not silently reactivated by this archive.

## Re-entry rule

A provider may return to canonical DGM-MAT only after:

1. real connectivity/execution is implemented;
2. health reflects observed reality, not configuration presence;
3. credentials remain governed by the vault/approval rules;
4. tests prove failure and success behavior against deterministic boundaries;
5. the provider has a real production caller;
6. provenance and ownership are documented.

This archive is historical evidence only. Do not auto-import, auto-execute, or auto-promote its contents.
