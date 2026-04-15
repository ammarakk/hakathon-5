import Link from "next/link";
import { MessageCircle, Mail, ShoppingBag, Clock, Sparkles } from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-pink-100 sticky top-0 z-50">
        <div className="container-custom py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-pink-500 to-purple-600 rounded-full flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gradient">Nur Scents</h1>
                <p className="text-xs text-gray-500">Premium Fragrances</p>
              </div>
            </div>
            <Link
              href="/support"
              className="bg-gradient-to-r from-pink-500 to-purple-600 text-white px-6 py-2 rounded-full font-medium hover:shadow-lg transition-all duration-300 hover:scale-105"
            >
              Get Support
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container-custom max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm mb-6">
            <Clock className="w-4 h-4 text-pink-500" />
            <span className="text-sm font-medium text-gray-700">24/7 Available</span>
          </div>

          <h2 className="text-5xl md:text-6xl font-bold mb-6">
            <span className="text-gradient">Welcome to Nur Scents</span>
            <br />
            <span className="text-gray-800">Customer Support</span>
          </h2>

          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto leading-relaxed">
            Experience premium fragrance support with our AI-powered assistant.
            Get instant help with orders, products, and any questions.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Link
              href="/support"
              className="group bg-gradient-to-r from-pink-500 to-purple-600 text-white px-8 py-4 rounded-full font-semibold text-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 flex items-center gap-2"
            >
              <MessageCircle className="w-5 h-5 group-hover:rotate-12 transition-transform" />
              Start Conversation
            </Link>
            <a
              href="https://wa.me/923001234567"
              target="_blank"
              rel="noopener noreferrer"
              className="bg-green-500 text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-green-600 transition-colors duration-300 flex items-center gap-2 hover:shadow-lg"
            >
              <MessageCircle className="w-5 h-5" />
              WhatsApp Us
            </a>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4 bg-white/50">
        <div className="container-custom max-w-6xl mx-auto">
          <h3 className="text-3xl font-bold text-center mb-12 text-gray-800">
            How Can We Help You?
          </h3>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-white rounded-2xl p-8 card-shadow hover:scale-105 transition-transform duration-300">
              <div className="w-14 h-14 bg-gradient-to-br from-pink-500 to-pink-600 rounded-xl flex items-center justify-center mb-4">
                <ShoppingBag className="w-7 h-7 text-white" />
              </div>
              <h4 className="text-xl font-bold mb-3 text-gray-800">
                Track Orders
              </h4>
              <p className="text-gray-600 leading-relaxed">
                Check your order status, get delivery updates, and track your package in real-time.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-white rounded-2xl p-8 card-shadow hover:scale-105 transition-transform duration-300">
              <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mb-4">
                <Mail className="w-7 h-7 text-white" />
              </div>
              <h4 className="text-xl font-bold mb-3 text-gray-800">
                Product Inquiries
              </h4>
              <p className="text-gray-600 leading-relaxed">
                Learn about our premium fragrances, get recommendations, and discover your perfect scent.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-white rounded-2xl p-8 card-shadow hover:scale-105 transition-transform duration-300">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mb-4">
                <MessageCircle className="w-7 h-7 text-white" />
              </div>
              <h4 className="text-xl font-bold mb-3 text-gray-800">
                Instant Support
              </h4>
              <p className="text-gray-600 leading-relaxed">
                Get immediate answers to your questions with our AI-powered assistant, available 24/7.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container-custom max-w-4xl mx-auto">
          <div className="bg-gradient-to-br from-pink-500 via-purple-500 to-blue-500 rounded-3xl p-12 text-center text-white shadow-2xl">
            <h3 className="text-3xl md:text-4xl font-bold mb-4">
              Need Help Right Now?
            </h3>
            <p className="text-lg mb-8 opacity-90 max-w-2xl mx-auto">
              Our AI assistant is ready to help you with any questions about orders, products, or services.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/support"
                className="bg-white text-purple-600 px-8 py-4 rounded-full font-semibold text-lg hover:bg-gray-100 transition-colors duration-300 shadow-lg"
              >
                Open Support Form
              </Link>
              <a
                href="mailto:support@nurscents.pk"
                className="bg-transparent border-2 border-white text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-white hover:text-purple-600 transition-all duration-300"
              >
                Email Us
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4">
        <div className="container-custom max-w-6xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-pink-500 to-purple-600 rounded-full flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-white" />
                </div>
                <h4 className="text-xl font-bold">Nur Scents</h4>
              </div>
              <p className="text-gray-400 text-sm leading-relaxed">
                Premium fragrances crafted with care. Bringing you the best perfumes from around the world.
              </p>
            </div>

            <div>
              <h5 className="font-semibold mb-4">Quick Links</h5>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li>
                  <Link href="/support" className="hover:text-white transition-colors">
                    Support
                  </Link>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Products
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    About Us
                  </a>
                </li>
              </ul>
            </div>

            <div>
              <h5 className="font-semibold mb-4">Contact Us</h5>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li>📍 Karachi, Pakistan</li>
                <li>📞 +92 300 1234567</li>
                <li>✉️ support@nurscents.pk</li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 text-center text-gray-400 text-sm">
            <p>&copy; 2026 Nur Scents. All rights reserved.</p>
            <p className="mt-2">Made with ❤️ in Karachi, Pakistan</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
