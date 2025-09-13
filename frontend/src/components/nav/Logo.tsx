type LogoProps = {
  className?: string;
};

const Logo = ({ className }: LogoProps): React.JSX.Element => (
  <span className={`${className} font-logo text-md tracking-wider select-none`}>
    GHOSTSWAP
  </span>
);

export default Logo;
