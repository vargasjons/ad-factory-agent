# Agency Swarm GitHub Template

A production-ready template for deploying [Agency Swarm](https://github.com/VRSEN/agency-swarm) agencies with Docker containerization and automated deployment to the [Agencii](https://agencii.ai/) cloud platform.

**🌐 [Agencii](https://agencii.ai/)** - The official cloud platform for Agency Swarm deployments  
**🔗 [GitHub App](https://github.com/apps/agencii)** - Automated deployment integration

---

## 🚀 Quick Start

### 1. Use This Template

Click **"Use this template"** to create your own repository, or:

```bash
git clone https://github.com/your-username/agency-github-template.git
cd agency-github-template
```

> **🌐 For Production**: Sign up at [agencii.ai](https://agencii.ai/) and use this template for automated cloud deployment

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Then edit `.env` with your actual API keys:

```bash
# Required: OpenAI API Key (for Sora video models and GPT agents)
OPENAI_API_KEY=sk-your-actual-key-here

# Required if using Veo: Google API Key
# Only needed if you select a Veo video generation model during onboarding
GOOGLE_API_KEY=your-actual-key-here
```

**Note**: The video generation model is selected during onboarding. Choose between:
- **Sora models** (OpenAI): Requires `OPENAI_API_KEY`
- **Veo models** (Google Gemini): Requires `GOOGLE_API_KEY`

### 4. Test the Example Agency

```bash
python agency.py
```

This runs the example agency in terminal mode for testing.

> **💡 Pro Tip**: For creating your own agency, open this template in [Cursor IDE](https://cursor.sh/) and use the AI assistant with the `.cursor/rules/workflow.mdc` file for automated agency creation!

---

## 🎨 Client Customization (Onboarding)

This agency is **fully productized** and can be easily customized for different clients!

### Quick Customization

```bash
# 1. Customize the agency for a new client
python onboarding_tool.py

# 2. Test your configuration
python test_onboarding.py

# 3. Run your customized agency
python agency.py
```

### What Can Be Customized?

- **Company Information**: Name, industry, brand voice
- **Target Audience**: Demographics and psychographics  
- **Product Category**: Type of products/services
- **Business Goals**: Primary and secondary objectives
- **Brand Guidelines**: Visual style, colors
- **Video Generation Model**: Select between Sora (OpenAI) or Veo (Google Gemini) models
- **Reasoning Effort**: Configure reasoning levels for each agent (low, medium, high)
- **Output Preferences**: Script format preferences

**Note**: All agents use GPT-5.1 model for optimal performance.

### Learn More

See **[ONBOARDING.md](ONBOARDING.md)** for complete customization guide including:
- Detailed configuration options
- Managing multiple client configs
- Best practices
- Advanced usage examples

---

## 🏗️ Project Structure

```
agency-github-template/
├── agency.py                 # Main entry point
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container configuration
├── .env                     # Environment variables (create this)
├── example_agent/           # Your agency folder
    ├── __init__.py
    ├── example_agent.py
    ├── instructions.md
    ├── files/               # Local files accessible to the agent (via files_folder)
    └── tools/
        └── ExampleTool.py
├── example_agent2/
├── agency_manifesto.md  # Shared instructions
├── requirements.txt
├── .env
└──...
```

---

## 🔧 Creating Your Own Agency

### 🤖 **AI-Assisted Agency Creation with Cursor**

This template includes **AI-powered agency creation** using Cursor IDE:

1. **Open this project in Cursor IDE**

2. **Use the AI Assistant** to create your agency by referencing:
   ```
   📁 .cursor/rules/workflow.mdc
   ```
3. **Simply ask the AI:**

   > "Create a new agency using the .cursor workflow"

   The AI will guide you through the complete 7-step process:

   - ✅ PRD Creation
   - ✅ Folder Structure Setup
   - ✅ Tool Development
   - ✅ Agent Creation
   - ✅ Agency Configuration
   - ✅ Testing & Validation
   - ✅ Iteration & Refinement

### 📋 **What the AI Will Do For You**

The AI assistant will automatically:

- Create proper folder structures
- Generate agent classes and instructions
- Build custom tools with full functionality
- Set up communication flows
- Create the main agency file
- Test everything to ensure it works

### 🚀 **Manual Alternative (Advanced Users)**

If you prefer manual setup, replace the `ExampleAgency/` folder with your own agency structure following the Agency Swarm conventions.

### Agency Structure Requirements

Your agency must follow this structure:

- **Agency Folder**: Contains all agents and manifesto
- **Agent Folders**: Each agent has its own folder with:
  - `AgentName.py` - Agent class definition
  - `instructions.md` - Agent-specific instructions
  - `tools/` - Folder containing agent tools
- **agency_manifesto.md** - Shared instructions for all agents

---

## 🚀 Production Deployment with Agencii

### **🌐 Deploy to Agencii Cloud Platform**

For production deployment, use the [Agencii](https://agencii.ai/) platform:

#### **Step 1: Create Account & Use Template**

1. **Sign up** at [agencii.ai](https://agencii.ai/)
2. **Use this template** to create your repository
3. **Develop your agency** using Cursor IDE with `.cursor` workflow

#### **Step 2: Install GitHub App**

1. **Install** the [Agencii GitHub App](https://github.com/apps/agencii)
2. **Grant permissions** to your repository
3. **Configure** environment variables in Agencii dashboard

#### **Step 3: Deploy**

1. **Push to main branch** - Agencii automatically detects and deploys
2. **Monitor deployment** in your Agencii dashboard
3. **Access your live agency** via provided endpoints

### **🔄 Automatic Deployments**

- **Auto-deploy** on every push to `main` branch
- **Zero-downtime** deployments with rollback capability
- **Environment management** through Agencii dashboard

---

## 🔨 Development Workflow

### **🎯 Recommended: AI-Assisted Development**

1. **Open Cursor IDE** with this template
2. **Ask the AI**: _"Create a new agency using the .cursor workflow"_
3. **Follow the guided process** - the AI handles everything automatically
4. **Test your agency**: `python agency.py`
5. **Deploy to production**: Install [Agencii GitHub App](https://github.com/apps/agencii) and push to main

### **⚙️ Manual Development (Advanced)**

If you prefer hands-on development:

1. **Create Tools**: Build agent tools in `tools/` folders
2. **Configure Agents**: Write `instructions.md` and agent classes
3. **Test Locally**: Run `python agency.py`
4. **Deploy**: Push to your preferred platform

The `.cursor/rules/workflow.mdc` file contains the complete development specifications for manual implementation.

---

## 📚 Key Features

- **🌐 Agencii Cloud Deploy**: One-click deployment to [Agencii platform](https://agencii.ai/)
- **🤖 AI-Assisted Creation**: Built-in Cursor IDE workflow for automated agency development
- **🔄 Auto-Deploy**: Automatic deployment on push to main branch
- **🚀 Ready-to-Deploy**: Dockerfile and requirements included
- **🔧 Modular Structure**: Easy to customize and extend
- **🛠️ Example Implementation**: Complete working example
- **📦 Container Ready**: Docker configuration for any platform
- **🔒 Environment Management**: Secure API key handling via Agencii dashboard
- **🧪 Local Testing**: Terminal demo for development
- **📋 Guided Workflow**: 7-step process with AI assistance

---

## 📖 Learn More

- **[Agency Swarm Documentation](https://agency-swarm.ai/)**
- **[Agency Swarm GitHub](https://github.com/VRSEN/agency-swarm)**

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## ⚡ Quick Tips

- **Start Small**: Begin with 1-2 agents and expand
- **Test Tools**: Each tool should work independently
- **Clear Instructions**: Write detailed agent instructions
- **Environment Setup**: Always use `.env` for API keys
- **Documentation**: Update instructions as you develop

---

**Ready to build your AI agency?** 🤖✨

### 🌐 **Production Route (Recommended)**

1. **Sign up** at [agencii.ai](https://agencii.ai/)
2. **Use this template** to create your repository
3. **Install** [Agencii GitHub App](https://github.com/apps/agencii)
4. **Push to main** → Automatic deployment!

### 🛠️ **Development Route**

Open this template in **Cursor IDE** and ask the AI to create your agency using the `.cursor` workflow. The AI will handle everything from setup to testing automatically!

For manual development, replace the `ExampleAgency` with your own implementation and start deploying intelligent agent systems!
