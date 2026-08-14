# ZUNEX BOT - Telegram Order Management System

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/ZUYANx/zunex-telegram-bot)
[![Python](https://img.shields.io/badge/python-3.7+-green.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](https://opensource.org/licenses/MIT)
[![Telegram](https://img.shields.io/badge/telegram-bot-blue.svg)](https://t.me/zunex_bot)

A powerful Telegram-based order management system with Steadfast shipping integration, SKU management, and automated reporting.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Commands](#commands)
6. [Order Format](#order-format)
7. [Configuration](#configuration)
8. [Project Structure](#project-structure)
9. [Storage Capacity](#storage-capacity)
10. [API Integration](#api-integration)
11. [Admin Tool](#admin-tool)
12. [Troubleshooting](#troubleshooting)
13. [License](#license)
14. [Contact](#contact)

---

## Overview

ZUNEX BOT is a complete Telegram-based order management solution designed for businesses of all sizes. It automatically detects orders, manages products (SKUs), integrates with Steadfast shipping API, and sends real-time reports to your team.

### Key Benefits

| Benefit | Description |
|---------|-------------|
| Automation | Auto-detects orders without manual entry |
| Shipping Integration | Auto-generates shipping labels |
| Team Reports | Real-time order notifications to your group |
| Product Management | Easy SKU management with images |
| Scalable | Handles 500,000+ orders in 1GB |
| Search & Track | Search by order number or phone |

---

## Features

### Core Features

| Feature | Description |
|---------|-------------|
| Auto-Order Detection | Works in groups and private chats |
| Smart Parser | Extracts data from any order format |
| Duplicate Prevention | Detects duplicate orders automatically |
| Inline Confirmation | Confirm/Cancel with inline buttons |
| Order History | Complete order database |
| Search Orders | By order number or phone |
| Today's Summary | View daily orders and totals |

### Product Management

| Feature | Description |
|---------|-------------|
| Add Products | /add command with wizard |
| Product Details | SKU, name, price, sizes, image |
| Image Upload | Upload via Telegram, stored on freeimage.host |
| View Products | /sku command with image |
| Auto-Generate SKU | Creates SKU from product name |

### Shipping Integration

| Feature | Description |
|---------|-------------|
| Steadfast API | Auto-send orders to Steadfast |
| Label Generation | Auto-generate shipping labels |
| Status Tracking | Shows SUCCESS/FAILED status |
| Admin Tool | Manage orders, check balance |

### Reporting

| Feature | Description |
|---------|-------------|
| Team Reports | Send orders to your group |
| Order Details | Complete order information |
| Label Links | Direct label download links |
| Steadfast Status | Real-time delivery status |

---

## Installation

### Option 1: One-Click Install (Recommended)

Copy and run these commands:

```bash
git clone https://github.com/ZUYANx/zunex-telegram-bot.git

cd zunex-telegram-bot

bash setup.sh

zunex
