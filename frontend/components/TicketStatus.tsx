"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "./ui/card";
import { getTicketStatus, SupportTicketResponse } from "@/lib/api";
import toast from "react-hot-toast";
import { formatDate } from "@/lib/utils";
import {
  CheckCircle,
  Clock,
  XCircle,
  AlertCircle,
  Search,
} from "lucide-react";

const ticketSchema = z.object({
  ticketId: z.string().min(1, "Please enter a ticket ID"),
});

type TicketFormData = z.infer<typeof ticketSchema>;

const statusConfig = {
  open: {
    icon: Clock,
    color: "text-blue-600",
    bgColor: "bg-blue-100",
    label: "Open",
    description: "We're working on your ticket",
  },
  in_progress: {
    icon: AlertCircle,
    color: "text-yellow-600",
    bgColor: "bg-yellow-100",
    label: "In Progress",
    description: "Our team is actively working on this",
  },
  resolved: {
    icon: CheckCircle,
    color: "text-green-600",
    bgColor: "bg-green-100",
    label: "Resolved",
    description: "Your ticket has been resolved",
  },
  closed: {
    icon: XCircle,
    color: "text-gray-600",
    bgColor: "bg-gray-100",
    label: "Closed",
    description: "This ticket has been closed",
  },
};

export function TicketStatus() {
  const [isLoading, setIsLoading] = useState(false);
  const [ticketData, setTicketData] = useState<SupportTicketResponse | null>(
    null
  );
  const [searched, setSearched] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<TicketFormData>({
    resolver: zodResolver(ticketSchema),
  });

  const onSubmit = async (data: TicketFormData) => {
    setIsLoading(true);

    try {
      const response = await getTicketStatus(data.ticketId);

      if (response.success && response.data) {
        setTicketData(response.data);
        setSearched(true);
        toast.success("Ticket found!");
      } else {
        toast.error(response.error || "Ticket not found");
        setTicketData(null);
      }
    } catch (error) {
      console.error("Ticket lookup error:", error);
      toast.error("Failed to lookup ticket. Please try again.");
      setTicketData(null);
    } finally {
      setIsLoading(false);
    }
  };

  const StatusIcon = ticketData
    ? statusConfig[ticketData.status as keyof typeof statusConfig]?.icon ||
      CheckCircle
    : CheckCircle;

  const statusInfo = ticketData
    ? statusConfig[ticketData.status as keyof typeof statusConfig]
    : null;

  return (
    <div className="w-full max-w-2xl mx-auto">
      <Card>
        <CardHeader>
          <CardTitle className="text-3xl">Check Ticket Status</CardTitle>
          <CardDescription className="text-base">
            Enter your ticket ID to see the current status of your support
            request.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <Input
                  label="Ticket ID"
                  placeholder="e.g., TKT_20250410123456"
                  error={errors.ticketId?.message}
                  {...register("ticketId")}
                />
              </div>
              <div className="flex items-end">
                <Button
                  type="submit"
                  isLoading={isLoading}
                  size="lg"
                  className="whitespace-nowrap"
                >
                  <Search className="w-4 h-4 mr-2" />
                  Check Status
                </Button>
              </div>
            </div>
          </form>

          {/* Ticket Status Display */}
          {searched && ticketData && (
            <div className="mt-8 animate-fade-in">
              <div
                className={`${statusInfo?.bgColor} border-l-4 border-current rounded-lg p-6 mb-6`}
              >
                <div className="flex items-start gap-4">
                  <div className={`${statusInfo?.color}`}>
                    <StatusIcon className="w-8 h-8" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-bold text-gray-900">
                        {ticketData.ticket_id}
                      </h3>
                      <span
                        className={`${statusInfo?.bgColor} ${statusInfo?.color} px-3 py-1 rounded-full text-xs font-semibold`}
                      >
                        {statusInfo?.label}
                      </span>
                    </div>
                    <p className="text-gray-700 mb-1">{statusInfo?.description}</p>
                    <p className="text-sm text-gray-600">
                      Created: {formatDate(ticketData.created_at)}
                    </p>
                  </div>
                </div>
              </div>

              {/* Response Message */}
              {ticketData.message && (
                <div className="bg-gray-50 rounded-lg p-6 mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3">
                    Latest Update:
                  </h4>
                  <p className="text-gray-700 leading-relaxed">
                    {ticketData.message}
                  </p>
                </div>
              )}

              {/* Estimated Response Time */}
              {ticketData.estimated_response_time && (
                <div className="bg-pink-50 border border-pink-200 rounded-lg p-4">
                  <div className="flex items-center gap-3">
                    <Clock className="w-5 h-5 text-pink-600" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        Expected Response Time
                      </p>
                      <p className="text-sm text-gray-600">
                        {ticketData.estimated_response_time}
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* No Ticket Found */}
          {searched && !ticketData && (
            <div className="mt-8 text-center animate-fade-in">
              <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <XCircle className="w-10 h-10 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Ticket Not Found
              </h3>
              <p className="text-gray-600 mb-6">
                We couldn't find a ticket with that ID. Please double-check
                and try again.
              </p>
              <Button
                variant="outline"
                onClick={() => {
                  setSearched(false);
                  reset();
                }}
              >
                Search Again
              </Button>
            </div>
          )}

          {/* Help Text */}
          {!searched && (
            <div className="mt-8 pt-6 border-t border-gray-200">
              <p className="text-sm text-gray-600 text-center">
                Can't find your ticket ID? Check your email or contact us at{" "}
                <a
                  href="mailto:support@nurscents.pk"
                  className="text-pink-600 hover:underline font-medium"
                >
                  support@nurscents.pk
                </a>
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
