# Schema.org JSON-LD Examples

Complete, copy-paste ready JSON-LD examples for common schema types. Use with the `<JsonLd>` component and `schema-dts` types.

## Organization (Every Site)

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://example.com/#organization",
  "name": "Your Company Name",
  "url": "https://example.com",
  "logo": {
    "@type": "ImageObject",
    "url": "https://example.com/logo.png",
    "width": 512,
    "height": 512
  },
  "description": "What your company does in one sentence.",
  "sameAs": [
    "https://twitter.com/yourcompany",
    "https://linkedin.com/company/yourcompany",
    "https://github.com/yourcompany"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+1-800-555-0100",
    "contactType": "customer service",
    "availableLanguage": ["English"]
  }
}
```

> **Note**: Google's Organization documentation (updated 2026-09) has no required properties and recommends as many relevant ones as apply: `legalName`, `alternateName`, `address`, `telephone`, `email`, `foundingDate`, `vatID` / `taxID` and `iso6523Code` (identification), and for online stores `hasMerchantReturnPolicy`, `hasShippingService` and `hasMemberProgram`. The `logo` must be at least 112x112 px and crawlable and indexable.

## WebSite (Home Page — Site Name)

Google uses `WebSite` `name` and `alternateName` for the site name shown in results. It reads this markup on the home page only:

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "url": "https://example.com/",
  "name": "Your Site Name",
  "alternateName": ["YSN", "yoursite.com"]
}
```

> **Note**: Do not add `SearchAction` for Google. The search box that used to appear under brand results was removed on 2024-11-21, and the markup no longer does anything in Google Search (it is harmless if it already exists). If you want to expose site search to non-Google consumers, `schema-dts` 2.x types it: `WithActionConstraints<SearchAction>` accepts `'query-input': 'required name=search_term_string'` without a type assertion.

## BreadcrumbList (All Inner Pages)

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://example.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Products",
      "item": "https://example.com/products"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Running Shoes",
      "item": "https://example.com/products/running-shoes"
    }
  ]
}
```

## Article / BlogPosting

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Your Article Headline (max 110 chars)",
  "description": "Short summary of the article in 1-2 sentences.",
  "image": "https://example.com/article-hero.jpg",
  "datePublished": "2026-03-15T09:00:00Z",
  "dateModified": "2026-03-20T14:30:00Z",
  "author": {
    "@type": "Person",
    "name": "Jane Smith",
    "url": "https://example.com/authors/jane-smith"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Your Site Name",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "https://example.com/blog/your-article"
  }
}
```

For news articles, change `@type` to `"NewsArticle"`.

## Product + Offer

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Ultra Running Shoes Pro",
  "image": [
    "https://example.com/shoes-front.jpg",
    "https://example.com/shoes-side.jpg"
  ],
  "description": "Lightweight trail running shoes with carbon-fiber plate.",
  "sku": "URS-PRO-001",
  "brand": {
    "@type": "Brand",
    "name": "SpeedRun"
  },
  "offers": {
    "@type": "Offer",
    "price": "149.99",
    "priceCurrency": "USD",
    "priceValidUntil": "2026-12-31",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition",
    "url": "https://example.com/products/ultra-running-shoes-pro",
    "seller": {
      "@type": "Organization",
      "name": "Your Store"
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.7",
    "reviewCount": "256"
  }
}
```

## Tutorials and Step Lists (no rich result)

Google removed the HowTo rich result on desktop and mobile (fully gone since September 2023) and has since removed its documentation, so no Google SERP feature comes from step markup anymore. Do not add that markup to win a result. Existing markup is harmless and can stay; for new tutorials, mark them up as `Article` / `TechArticle` (see Article / BlogPosting above) and make the steps visible content: an ordered list (`<ol>`) under clear headings, with one action per step.

## Event

Only for genuine, publicly verifiable events:

```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "Annual Tech Summit 2026",
  "description": "Two-day conference covering AI, cloud, and developer tools.",
  "startDate": "2026-06-15T09:00:00+00:00",
  "endDate": "2026-06-16T18:00:00+00:00",
  "eventStatus": "https://schema.org/EventScheduled",
  "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
  "location": {
    "@type": "Place",
    "name": "Convention Center",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "500 Convention Blvd",
      "addressLocality": "San Francisco",
      "addressRegion": "CA",
      "addressCountry": "US"
    }
  },
  "organizer": {
    "@type": "Organization",
    "name": "TechEvents Inc.",
    "url": "https://techevents.example.com"
  },
  "offers": {
    "@type": "Offer",
    "price": "299",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "validFrom": "2026-01-01T00:00:00Z",
    "url": "https://techevents.example.com/tickets"
  },
  "image": "https://techevents.example.com/summit-banner.jpg"
}
```

## LocalBusiness

```json
{
  "@context": "https://schema.org",
  "@type": "Restaurant",
  "name": "The Corner Bistro",
  "image": "https://example.com/bistro.jpg",
  "url": "https://cornerbistro.example.com",
  "telephone": "+1-555-0100",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main Street",
    "addressLocality": "Austin",
    "addressRegion": "TX",
    "postalCode": "78701",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 30.2672,
    "longitude": -97.7431
  },
  "openingHoursSpecification": [
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
      "opens": "11:00",
      "closes": "22:00"
    },
    {
      "@type": "OpeningHoursSpecification",
      "dayOfWeek": ["Saturday", "Sunday"],
      "opens": "10:00",
      "closes": "23:00"
    }
  ],
  "priceRange": "$$",
  "servesCuisine": "American",
  "acceptsReservations": "true"
}
```

## SoftwareApplication

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "Your App Name",
  "operatingSystem": "Web",
  "applicationCategory": "DeveloperApplication",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "ratingCount": 1024
  }
}
```

## Implementation Priority

1. **Every site (root layout):** Organization; **home page:** WebSite (`name` / `alternateName`) for the site name
2. **All inner pages:** BreadcrumbList
3. **Blog/news:** Article or NewsArticle (also for tutorials)
4. **E-commerce:** Product + Offer + AggregateRating
5. **Events:** Event (genuine, verifiable events only)
6. **Local business:** LocalBusiness with geo + hours
7. **Skip for SERP purposes:** FAQPage and HowTo (both rich results removed from Google Search — FAQ on 2026-05-07, HowTo in 2023) and `SearchAction` (search box removed 2024-11-21). Markup that already exists is harmless
