import { Product } from "@/lib/api";
import { Card, CardContent, CardFooter } from "./ui/card";
import { Button } from "./ui/button";
import { formatCurrency } from "@/lib/utils";
import { Sparkles, Package, TrendingUp } from "lucide-react";

interface ProductCardProps {
  product: Product;
  onViewDetails?: (product: Product) => void;
  onAddToOrder?: (product: Product) => void;
}

export function ProductCard({
  product,
  onViewDetails,
  onAddToOrder,
}: ProductCardProps) {
  const isOutOfStock = product.stock === 0;
  const isLowStock = product.stock > 0 && product.stock <= 5;

  return (
    <Card className="group hover:shadow-xl transition-all duration-300 overflow-hidden">
      {/* Product Image */}
      <div className="relative h-48 bg-gradient-to-br from-pink-50 to-purple-50 overflow-hidden">
        {product.image_url ? (
          <img
            src={product.image_url}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Sparkles className="w-16 h-16 text-pink-300" />
          </div>
        )}

        {/* Stock Badge */}
        {isOutOfStock && (
          <div className="absolute top-3 right-3 bg-red-500 text-white px-3 py-1 rounded-full text-xs font-semibold">
            Out of Stock
          </div>
        )}
        {isLowStock && (
          <div className="absolute top-3 right-3 bg-orange-500 text-white px-3 py-1 rounded-full text-xs font-semibold">
            Only {product.stock} left
          </div>
        )}

        {/* Category Badge */}
        <div className="absolute top-3 left-3 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-medium text-gray-700">
          {product.category}
        </div>
      </div>

      <CardContent className="p-4">
        {/* Product Name */}
        <h3 className="font-bold text-lg text-gray-900 mb-2 line-clamp-2">
          {product.name}
        </h3>

        {/* Product Description */}
        <p className="text-sm text-gray-600 mb-3 line-clamp-2">
          {product.description}
        </p>

        {/* Fragrance Notes */}
        {product.fragrance_notes && product.fragrance_notes.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {product.fragrance_notes.slice(0, 3).map((note, index) => (
              <span
                key={index}
                className="bg-pink-50 text-pink-700 px-2 py-1 rounded text-xs font-medium"
              >
                {note}
              </span>
            ))}
          </div>
        )}

        {/* Price and Details */}
        <div className="flex items-center justify-between mb-3">
          <div>
            <p className="text-2xl font-bold text-pink-600">
              {formatCurrency(product.price)}
            </p>
            {product.size && (
              <p className="text-xs text-gray-500">{product.size}</p>
            )}
          </div>
          {product.gender && (
            <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-xs font-semibold">
              {product.gender}
            </span>
          )}
        </div>

        {/* Stock Info */}
        {!isOutOfStock && (
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Package className="w-4 h-4" />
            <span>{product.stock} in stock</span>
          </div>
        )}
      </CardContent>

      <CardFooter className="p-4 pt-0 gap-2">
        {onViewDetails && (
          <Button
            variant="outline"
            onClick={() => onViewDetails(product)}
            className="flex-1"
            size="sm"
          >
            View Details
          </Button>
        )}
        {onAddToOrder && !isOutOfStock && (
          <Button
            onClick={() => onAddToOrder(product)}
            className="flex-1"
            size="sm"
          >
            Add to Order
          </Button>
        )}
      </CardFooter>
    </Card>
  );
}

interface ProductGridProps {
  products: Product[];
  onViewDetails?: (product: Product) => void;
  onAddToOrder?: (product: Product) => void;
  loading?: boolean;
}

export function ProductGrid({
  products,
  onViewDetails,
  onAddToOrder,
  loading = false,
}: ProductGridProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {[...Array(8)].map((_, index) => (
          <Card key={index} className="animate-pulse">
            <div className="h-48 bg-gray-200" />
            <CardContent className="p-4 space-y-3">
              <div className="h-5 bg-gray-200 rounded" />
              <div className="h-4 bg-gray-200 rounded" />
              <div className="h-6 bg-gray-200 rounded w-1/2" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Package className="w-10 h-10 text-gray-400" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          No Products Found
        </h3>
        <p className="text-gray-600">
          Try adjusting your search or filter criteria
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          onViewDetails={onViewDetails}
          onAddToOrder={onAddToOrder}
        />
      ))}
    </div>
  );
}
