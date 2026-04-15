"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Select } from "./ui/select";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "./ui/card";
import { submitSupportForm, SupportFormData } from "@/lib/api";
import toast from "react-hot-toast";
import { MessageCircle, Mail, Phone, MapPin, Clock } from "lucide-react";

// Form validation schema
const supportSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email address"),
  phone: z
    .string()
    .min(10, "Phone number must be at least 10 digits")
    .regex(/^[0-9+\s-]+$/, "Please enter a valid phone number"),
  category: z.string().min(1, "Please select a category"),
  subject: z.string().min(5, "Subject must be at least 5 characters"),
  message: z.string().min(10, "Message must be at least 10 characters"),
  order_number: z.string().optional(),
});

type SupportFormData = z.infer<typeof supportSchema>;

const categories = [
  { value: "", label: "Select a category" },
  { value: "order_inquiry", label: "Order Inquiry" },
  { value: "product_question", label: "Product Question" },
  { value: "payment_issue", label: "Payment Issue" },
  { value: "shipping", label: "Shipping & Delivery" },
  { value: "return_refund", label: "Return & Refund" },
  { value: "complaint", label: "Complaint" },
  { value: "feedback", label: "Feedback" },
  { value: "other", label: "Other" },
];

export function SupportForm() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [ticketId, setTicketId] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<SupportFormData>({
    resolver: zodResolver(supportSchema),
    mode: "onBlur",
  });

  const onSubmit = async (data: SupportFormData) => {
    setIsSubmitting(true);

    try {
      const response = await submitSupportForm(data as any);

      if (response.success && response.data) {
        toast.success("Support ticket created successfully!");
        setTicketId(response.data.ticket_id);
        setSubmitted(true);
        reset();
      } else {
        toast.error(response.error || "Failed to create support ticket");
      }
    } catch (error) {
      console.error("Form submission error:", error);
      toast.error("An unexpected error occurred. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitted && ticketId) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardContent className="pt-6">
          <div className="text-center py-8">
            <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg
                className="w-10 h-10 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </div>

            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              Thank You!
            </h3>
            <p className="text-gray-600 mb-6">
              Your support ticket has been created successfully.
            </p>

            <div className="bg-pink-50 border border-pink-200 rounded-lg p-6 mb-6">
              <p className="text-sm text-gray-600 mb-2">Your Ticket ID:</p>
              <p className="text-2xl font-bold text-pink-600">{ticketId}</p>
            </div>

            <p className="text-sm text-gray-600 mb-6">
              We'll get back to you within 24 hours. You can also reach us
              directly:
            </p>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <a
                href="https://wa.me/923001234567"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 bg-green-50 text-green-700 px-4 py-3 rounded-lg hover:bg-green-100 transition-colors"
              >
                <MessageCircle className="w-5 h-5" />
                <span className="font-medium">WhatsApp</span>
              </a>
              <a
                href="tel:+923001234567"
                className="flex items-center justify-center gap-2 bg-blue-50 text-blue-700 px-4 py-3 rounded-lg hover:bg-blue-100 transition-colors"
              >
                <Phone className="w-5 h-5" />
                <span className="font-medium">Call Us</span>
              </a>
              <a
                href="mailto:support@nurscents.pk"
                className="flex items-center justify-center gap-2 bg-purple-50 text-purple-700 px-4 py-3 rounded-lg hover:bg-purple-100 transition-colors"
              >
                <Mail className="w-5 h-5" />
                <span className="font-medium">Email</span>
              </a>
            </div>

            <Button
              onClick={() => {
                setSubmitted(false);
                setTicketId(null);
              }}
              variant="outline"
            >
              Submit Another Ticket
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="text-3xl">Get Support</CardTitle>
          <CardDescription className="text-base">
            Fill out the form below and our AI assistant will help you right
            away.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Name */}
            <Input
              label="Full Name"
              placeholder="Enter your full name"
              error={errors.name?.message}
              {...register("name")}
            />

            {/* Email */}
            <Input
              label="Email Address"
              type="email"
              placeholder="your.email@example.com"
              error={errors.email?.message}
              {...register("email")}
            />

            {/* Phone */}
            <Input
              label="Phone Number"
              type="tel"
              placeholder="+92 300 1234567"
              error={errors.phone?.message}
              {...register("phone")}
            />

            {/* Category */}
            <Select
              label="Category"
              options={categories}
              error={errors.category?.message}
              {...register("category")}
            />

            {/* Order Number (Optional) */}
            <Input
              label="Order Number (Optional)"
              placeholder="If your question is about an order"
              error={errors.order_number?.message}
              {...register("order_number")}
            />

            {/* Subject */}
            <Input
              label="Subject"
              placeholder="Brief summary of your inquiry"
              error={errors.subject?.message}
              {...register("subject")}
            />

            {/* Message */}
            <Textarea
              label="Message"
              rows={6}
              placeholder="Please describe your inquiry in detail..."
              error={errors.message?.message}
              {...register("message")}
            />

            {/* Submit Button */}
            <div className="flex flex-col sm:flex-row gap-4">
              <Button
                type="submit"
                isLoading={isSubmitting}
                className="flex-1"
                size="lg"
              >
                Submit Ticket
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => reset()}
                disabled={isSubmitting}
                size="lg"
              >
                Clear Form
              </Button>
            </div>
          </form>

          {/* Alternative Contact Methods */}
          <div className="mt-8 pt-8 border-t border-gray-200">
            <p className="text-sm text-gray-600 text-center mb-4">
              Prefer to contact us directly?
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <a
                href="https://wa.me/923001234567"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 bg-green-50 text-green-700 px-4 py-3 rounded-lg hover:bg-green-100 transition-colors text-sm font-medium"
              >
                <MessageCircle className="w-4 h-4" />
                WhatsApp
              </a>
              <a
                href="tel:+923001234567"
                className="flex items-center justify-center gap-2 bg-blue-50 text-blue-700 px-4 py-3 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium"
              >
                <Phone className="w-4 h-4" />
                Call Now
              </a>
              <a
                href="mailto:support@nurscents.pk"
                className="flex items-center justify-center gap-2 bg-purple-50 text-purple-700 px-4 py-3 rounded-lg hover:bg-purple-100 transition-colors text-sm font-medium"
              >
                <Mail className="w-4 h-4" />
                Email Us
              </a>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Contact Info Card */}
      <Card className="mt-6">
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
            <div className="flex flex-col items-center">
              <div className="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center mb-3">
                <Clock className="w-6 h-6 text-pink-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-1">
                Response Time
              </h4>
              <p className="text-sm text-gray-600">
                Usually within minutes
              </p>
            </div>

            <div className="flex flex-col items-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-3">
                <MapPin className="w-6 h-6 text-purple-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-1">Location</h4>
              <p className="text-sm text-gray-600">Karachi, Pakistan</p>
            </div>

            <div className="flex flex-col items-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-3">
                <MessageCircle className="w-6 h-6 text-blue-600" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-1">24/7 Support</h4>
              <p className="text-sm text-gray-600">
                Always here to help
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
