"use client";

import { useState } from "react";
import Link from "next/link";
import { SupportForm } from "@/components/SupportForm";
import { TicketStatus } from "@/components/TicketStatus";
import { Sparkles, MessageCircle, Home, Search, FileText } from "lucide-react";

export default function SupportPage() {
  const [activeTab, setActiveTab] = useState<"form" | "status">("form");

  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-pink-100 sticky top-0 z-50">
        <div className="container-custom py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-pink-500 to-purple-600 rounded-full flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gradient">Nur Scents</h1>
                <p className="text-xs text-gray-500">Customer Support</p>
              </div>
            </Link>

            <nav className="hidden md:flex items-center gap-6">
              <Link
                href="/"
                className="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <Home className="w-4 h-4" />
                Home
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-12 px-4 bg-gradient-to-br from-pink-50 via-purple-50 to-blue-50">
        <div className="container-custom max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm mb-6">
            <MessageCircle className="w-4 h-4 text-pink-500" />
            <span className="text-sm font-medium text-gray-700">
              24/7 Support Available
            </span>
          </div>

          <h2 className="text-4xl md:text-5xl font-bold mb-4">
            <span className="text-gradient">How Can We Help?</span>
          </h2>

          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Get instant support for your orders, product inquiries, and any
            questions. Our AI assistant is ready to help you 24/7.
          </p>
        </div>
      </section>

      {/* Tab Navigation */}
      <section className="py-8 px-4 bg-white border-b border-gray-200">
        <div className="container-custom max-w-2xl mx-auto">
          <div className="flex bg-gray-100 rounded-full p-1">
            <button
              onClick={() => setActiveTab("form")}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-6 rounded-full font-medium transition-all duration-200 ${
                activeTab === "form"
                  ? "bg-white text-pink-600 shadow-sm"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              <FileText className="w-4 h-4" />
              Submit Ticket
            </button>
            <button
              onClick={() => setActiveTab("status")}
              className={`flex-1 flex items-center justify-center gap-2 py-3 px-6 rounded-full font-medium transition-all duration-200 ${
                activeTab === "status"
                  ? "bg-white text-pink-600 shadow-sm"
                  : "text-gray-600 hover:text-gray-900"
              }`}
            >
              <Search className="w-4 h-4" />
              Check Status
            </button>
          </div>
        </div>
      </section>

      {/* Content Section */}
      <section className="py-12 px-4">
        <div className="container-custom">
          {activeTab === "form" && <SupportForm />}
          {activeTab === "status" && <TicketStatus />}
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-12 px-4 bg-gray-50">
        <div className="container-custom max-w-4xl mx-auto">
          <h3 className="text-3xl font-bold text-center mb-8 text-gray-900">
            Frequently Asked Questions
          </h3>

          <div className="grid md:grid-cols-2 gap-6">
            <FAQCard
              question="How quickly will I get a response?"
              answer="Our AI assistant responds instantly! For complex issues that need human attention, we typically respond within 24 hours."
            />
            <FAQCard
              question="Can I track my order here?"
              answer="Yes! Use the 'Check Status' tab and enter your order number to track your delivery in real-time."
            />
            <FAQCard
              question="What payment methods do you accept?"
              answer="We accept Cash on Delivery (COD), bank transfers, JazzCash, EasyPaisa, and all major credit/debit cards."
            />
            <FAQCard
              question="Do you ship outside Karachi?"
              answer="Currently, we primarily serve Karachi with zone-based delivery. Contact us for other cities."
            />
            <FAQCard
              question="How can I return or exchange a product?"
              answer="Returns are accepted within 7 days of delivery if the product is unopened. Contact us via WhatsApp or email to initiate a return."
            />
            <FAQCard
              question="Are your perfumes authentic?"
              answer="Absolutely! All our fragrances are 100% authentic and sourced directly from authorized distributors."
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4">
        <div className="container-custom max-w-4xl mx-auto">
          <div className="bg-gradient-to-br from-pink-500 via-purple-500 to-blue-500 rounded-3xl p-12 text-center text-white shadow-2xl">
            <h3 className="text-3xl md:text-4xl font-bold mb-4">
              Still Have Questions?
            </h3>
            <p className="text-lg mb-8 opacity-90 max-w-2xl mx-auto">
              Don't worry! Our support team is here to help. Reach out to us
              directly through your preferred channel.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="https://wa.me/923001234567"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-green-500 text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-green-600 transition-colors duration-300 flex items-center justify-center gap-2 shadow-lg"
              >
                <MessageCircle className="w-5 h-5" />
                WhatsApp Us
              </a>
              <a
                href="mailto:support@nurscents.pk"
                className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-white hover:text-purple-600 transition-all duration-300 flex items-center justify-center"
              >
                Email Support
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 px-4">
        <div className="container-custom max-w-6xl mx-auto text-center">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-10 h-10 bg-gradient-to-br from-pink-500 to-purple-600 rounded-full flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <h4 className="text-xl font-bold">Nur Scents</h4>
          </div>
          <p className="text-gray-400 text-sm mb-4">
            Premium fragrances crafted with care in Karachi, Pakistan
          </p>
          <div className="flex justify-center gap-6 text-sm text-gray-400">
            <a href="#" className="hover:text-white transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-white transition-colors">
              Terms of Service
            </a>
            <a href="#" className="hover:text-white transition-colors">
              Contact
            </a>
          </div>
          <div className="mt-6 pt-6 border-t border-gray-800 text-gray-400 text-sm">
            <p>&copy; 2026 Nur Scents. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

function FAQCard({
  question,
  answer,
}: {
  question: string;
  answer: string;
}) {
  return (
    <div className="bg-white rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow duration-300">
      <h4 className="font-bold text-gray-900 mb-2">{question}</h4>
      <p className="text-sm text-gray-600 leading-relaxed">{answer}</p>
    </div>
  );
}
