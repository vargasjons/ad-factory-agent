# Ad Creator Agency

An AI-powered ad agency that creates 100% AI-generated UGC-style video ads. Everything from market research to scripting and video generation is done completely autonomously.

[![Watch Demo Video](https://img.youtube.com/vi/X4NjNCSiqjs/maxresdefault.jpg)](https://youtu.be/X4NjNCSiqjs)

> **Deploy this agency in 60 seconds on our platform:** [https://agencii.ai/marketplace/GEauD3kFGVy5NjaTy3w5/](https://agencii.ai/marketplace/GEauD3kFGVy5NjaTy3w5/)

---

## 🎯 What Makes This Different?

Unlike typical ad creation tools or generic AI copywriters, this agency:

- **Trained on a real $2.5M+ process** - Built on proven methods from an e-commerce agency that generated over $2.5 million with Sora ads
- **Iterative, not just automated** - Unlike simple automation, refine results based on feedback—replace segments, adjust subtitles, remix videos as needed
- **Full end-to-end workflow** - From deep market research to final rendered video with subtitles, completely autonomous
- **Belief-driven strategy** - Creates 4 foundational research documents that identify the exact beliefs driving purchase decisions
- **Production-ready workflow** - Organizes videos by folders like a real video editor, generates videos in parallel for speed

---

## ✨ How It Works

### Three AI Agents, One Complete System

**1. Strategy Agent** - The Foundation Builder

- Asks questions about your product, target audience, and brand positioning
- Performs web searches and analyzes your website/competitors
- Creates 4 foundational research documents (saved to organized folders):
  - Comprehensive market research
  - Customer avatar profiles with beliefs framework
  - Offer brief with unique mechanism
  - Necessary beliefs that drive purchases

**2. Brand Agent** - The Copywriter

- Generates argument-driven ad scripts and shot-by-shot storyboards
- Allows you to iterate and refine (adjust length, tone, style) before video generation
- Transfers you to the UGC Agent only after you approve the storyboard

**3. UGC Agent** - The Video Producer

- Generates product images with your branding for reference
- Creates comprehensive video prompts and generates videos in parallel (saves time)
- Lets you refine results: replace segments, trim clips, adjust subtitles, add logos
- Combines segments with transitions and subtitles for final ready-to-use videos

### The Result

Professional UGC-style video ads grounded in direct response strategy and powered by belief-based copywriting. Each ad systematically moves viewers toward an inevitable purchase decision.

### Why This Beats Simple Automation

Unlike automation that "spits out a video and calls it a day," this agency works like a real team:

- **Iterative feedback loops** at every stage (research, storyboard, video)
- **Refine any element**: Replace segments, adjust timing, modify subtitles, add brand assets
- **Persistent memory**: All research documents saved to organized folders for reuse
- **Real production workflow**: Just like working with a video editor, not a black box

---

## 💼 Perfect For

Marketing agencies, DTC brands, course creators, SaaS companies who need:

- A scalable system for creating high-converting video ads
- The ability to test multiple ad variations quickly
- Professional results without hiring creators
- White-labeled solution to resell to clients

---

## 🎨 What You'll Need

- **OpenAI API Key** - For GPT-5.1 agents and Sora 2 video models ([get it here](https://platform.openai.com))
- **Google API Key** - For nano banana ([get it here](https://aistudio.google.com))
- **Product/Brand Information** - The Strategy Agent guides you through questions about your audience, positioning, and brand voice

---

## 🚀 Getting Started

### Option 1: Deploy on Agencii (Recommended)

1. Go to [Agencii Marketplace](https://agencii.ai/marketplace) and find the "UGC Ad Factory Agent"
2. Click **Deploy** and fill out the onboarding form:
   - Company/brand name
   - Video model preference (Sora 2, Sora 2 Pro, or Veo 3.1)
   - Upload brand assets (logo, guidelines)
   - Add your `OPENAI_API_KEY` and `GOOGLE_API_KEY` (get them from [platform.openai.com](https://platform.openai.com) and [Google AI Studio](https://aistudio.google.com))
3. **Enable persistent file storage** (critical for saving research documents across chats)
4. Deploy into a Custom GPT for your white-labeled web application

Your agency will be ready in ~60 seconds.

### Option 2: Run Locally

```bash
# 1. Clone and install
git clone https://github.com/your-repo/ad-factory-agent.git
cd ad-factory-agent
pip install -r requirements.txt

# 2. Set up your API keys
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# 3. Run the agency
python agency.py
```

## 🔄 How to Use It

### Creating Your First Ad

**Step 1: Start a conversation**

```
User: "I want to create ads for my hot sauce"
```

**Step 2: Strategy Agent asks questions** (use transcription mode for faster input)

The agent asks about:

- Product role in your business
- Target audience (be specific: "marketing agency owners making $500K+")
- Brand voice and positioning
- Website URL (for automatic research)

**Step 3: Automatic deep research** (~2-3 minutes)

The agent:

- Performs web searches and analyzes your website
- Studies competitors and market positioning
- Creates 4 foundational documents saved to organized folders:
  - Market research (6+ pages)
  - Customer avatar with beliefs framework
  - Offer brief with unique mechanism
  - Necessary beliefs document

**Step 4: Review and approve storyboard**

BrandAgent creates:

- Argument-driven script (you can request adjustments: "make it funnier," "shorten to 30 seconds")
- Shot-by-shot storyboard
- You iterate until it's perfect, then approve

**Step 5: Video generation and refinement**

UGCAgent:

- Generates product images with your branding
- Creates video prompts and generates videos in parallel
- You can refine: "replace segment 2," "trim 1 second off the end," "add my logo," "make subtitles yellow"
- Combines final segments with subtitles into ready-to-use MP4

### Creating More Ads for the Same Product

```
User: "Create 3 more ad variations for [Product Name]"
```

The agency reads your existing research documents from storage and immediately creates new scripts—no re-explaining needed.

---

## 🔐 Customization & White-Labeling

The agency includes a simple onboarding tool for client customization:

```bash
python onboarding_tool.py
```

Configure:

- Company/brand name
- Visual brand guidelines
- Preferred video generation model (Sora vs Veo)

Product-specific details (audience, goals, positioning) are gathered conversationally by the Strategy Agent for each new product—ensuring information is always fresh and relevant.

---

## 🛠️ Advanced: How It's Built

### Powered by Agency Swarm

Built on [Agency Swarm](https://github.com/VRSEN/agency-swarm), the open-source framework for creating collaborative AI agent systems.

### Trained on Real $2.5M+ Process

This agency was trained on the actual workflow of an e-commerce agency that generated over $2.5 million with Sora ads. We extracted their 5-step process, including foundational documents and research templates, and built agents that follow the exact same methodology.

### Model: GPT-5.1 with Reasoning

All agents use GPT-5.1 (o4-mini) with medium reasoning effort for optimal strategic thinking and copywriting quality (noticeably funnier and more creative than GPT-5).

### Video Generation

Choose between:

- **Sora 2 / Sora 2 Pro** (OpenAI) - Highest quality, best for complex scenes
- **Veo 3.1** (Google Gemini) - Fast generation, great for high-volume production

### Open Source

Full code available for customization, white-labeling, and extension. Fork it, modify it, make it yours.

---

## 💰 Cost & Limitations

### Typical Costs

For a 30-second UGC ad, expect approximately **$9 in API costs**:

- **Sora 2**: ~$0.10/second ($8-9 for video generation + $1 for agent reasoning)
- **Sora 2 Pro**: ~$0.30/second (higher quality, longer generation time)
- **Veo 3.1**: Lower cost, faster generation

While this may seem high, it's significantly cheaper than hiring creators and allows you to test many more ad variations.

### Current Limitations

- **Character consistency**: Due to OpenAI safety policies, you cannot currently pass face images as reference to Sora 2 (product consistency works perfectly)
- **Token costs**: Video generation is the primary cost driver

---

## 🔮 Roadmap

**Coming Soon:**

- **Enhanced subtitles** - TikTok-style animated subtitles with custom styling
- **Video overlays** - Add B-roll footage with voiceovers
- **Character consistency** - Once OpenAI enables face reference images for Sora
- A/B testing recommendations based on belief framework
- Integration with ad platforms (Facebook, TikTok, YouTube)

**In Development:**

- Multi-language support
- Extended video lengths (up to 60 seconds)
- Image-based ads (static and carousel formats)

---

## 💬 Get Support

Questions? Need help with this agency?

**Join our community:** [skool.com/agency-ai](https://skool.com/agency-ai)

---

## 🚀 Ready to Deploy?

**No credit card required to get started.**

Deploy on [Agencii](https://agencii.ai/marketplace/GEauD3kFGVy5NjaTy3w5/) → Fill the form → Start creating ads in 60 seconds.

**Your AI ad agency is waiting.**
