# Proto: Drawing to Code

**Proto** is a comprehensive full-stack web application designed to automate the conversion of UI sketches and textual descriptions into functional, production-ready frontend code. By leveraging a sophisticated **Retrieval-Augmented Generation (RAG)** pipeline, Proto ensures that AI-generated code is grounded in real-world design patterns and proven UI components.

---

## 🚀 Overview
The modern development lifecycle is often slowed down by the manual translation of visual ideas into code. Proto bridges this gap using multimodal Large Language Models (LLMs) to interpret visual layouts directly from user inputs—ranging from hand-drawn sketches to high-fidelity wireframes.

### Key Features
* **Multimodal Analysis**: Decomposes UI screenshots and sketches into semantic layout descriptions.
* **Contextual RAG**: Indexes the **pix2code** dataset to provide high-quality "reference examples" to the LLM.
* **Framework Versatility**: Supports code generation for **React, Vue, Angular**, and plain **HTML**.
* **Production-Ready**: Utilizes **Tailwind CSS** to ensure generated code is clean and responsive.

---

## 🏗️ System Architecture
The system operates through a multi-stage pipeline:
1.  **Visual Analysis Phase**: The FastAPI backend sends the user's image to **Gemini 3 Flash** to generate a semantic UI layout description.
2.  **RAG Retrieval Pipeline**: The description is used as a semantic query against a **ChromaDB** vector store to retrieve relevant code examples.
3.  **Code Synthesis Phase**: A final prompt, augmented with the retrieved context and original image, is processed to produce the final code.
4.  **Persistence**: Project metadata and generated snippets are stored in **MongoDB**.

---

## 🛠️ Tech Stack
* **Frontend**: React, Tailwind CSS, Shadcn UI
* **Backend**: FastAPI
* **AI/ML**: Gemini 3 Flash (Multimodal LLM)
* **Vector Database**: ChromaDB
* **Database**: MongoDB (via Motor async driver)
* **Dataset**: pix2code

---

## 📸 Visuals
* **System Architecture**:<img width="1582" height="3688" alt="image" src="https://github.com/user-attachments/assets/9b34004d-c1e6-4e85-af9d-2813fffaa566" />
* **Train Tab**:<img width="1846" height="1296" alt="image" src="https://github.com/user-attachments/assets/a7a4c403-d75e-4562-aaa2-b4a0cfed1699" />
* **Generate**:<img width="1846" height="983" alt="image" src="https://github.com/user-attachments/assets/16bff0cd-775d-4e54-8468-e09c68e1683a" />
* **Output**:<img width="1846" height="977" alt="image" src="https://github.com/user-attachments/assets/7e4fe438-8b52-4751-81e4-2e0809d98511" />
* **Preview of Generated Frontend code on this link -> playcode.io/new**:<img width="670" height="625" alt="image" src="https://github.com/user-attachments/assets/32715747-914d-435b-8b35-e68f9eebfdc9" />
---

## 🔮 Future Scope
* **Dataset Expansion**: Integration of Rico, WebSight, and VISION2UI datasets.
* **Advanced Embeddings**: Implementing CLIP-based models for direct image-to-image similarity searches.
* **Live Sandbox**: An integrated environment for real-time interactive previews.
* **Enterprise Customization**: Support for internal design system fine-tuning.

---

## 👥 Team
* **Ashirwad Singh**: Full-stack implementation and RAG pipeline development.
* **Samarth Gupta**: Collaborative development and system architecture.
* **Mentor**: Shri. Keshan Srivastava

---

## 📚 References
1. Beltramelli, T. (2017). *pix2code: Generating Code from a Graphical User Interface Screenshot*.
2. Nozomu. *pix2code-data Dataset*. HuggingFace.
